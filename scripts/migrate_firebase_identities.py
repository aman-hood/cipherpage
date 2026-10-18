"""Safely attach explicitly verified Firebase accounts to existing user rows.

Run from ``backend`` with its normal environment. The default mode only validates
the CSV shape. Applying requires ``--apply`` and never matches accounts by email.
"""

import argparse
import csv
import sys
from pathlib import Path


ALLOWED_METHODS = {"reauthenticated", "support_verified", "identity_provider_export"}
REQUIRED_COLUMNS = {
    "legacy_auth_uid",
    "firebase_uid",
    "verification_method",
    "evidence_ref",
}


def read_mappings(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        if not reader.fieldnames or not REQUIRED_COLUMNS.issubset(reader.fieldnames):
            raise ValueError("CSV must contain the required identity and verification columns")
        rows = []
        for row_number, row in enumerate(reader, start=2):
            item = {key: (row.get(key) or "").strip() for key in REQUIRED_COLUMNS}
            if not all(item.values()):
                raise ValueError(f"CSV row {row_number} has an empty required field")
            if item["verification_method"] not in ALLOWED_METHODS:
                raise ValueError(f"CSV row {row_number} uses an unsupported verification method")
            rows.append(item)

    legacy_uids = [row["legacy_auth_uid"] for row in rows]
    firebase_uids = [row["firebase_uid"] for row in rows]
    if len(legacy_uids) != len(set(legacy_uids)) or len(firebase_uids) != len(set(firebase_uids)):
        raise ValueError("CSV contains duplicate legacy or Firebase UIDs")
    return rows


def validate_firebase_account(firebase_auth, app, firebase_uid: str):
    """Require a live, email-verified Firebase account in the configured project."""
    firebase_user = firebase_auth.get_user(firebase_uid, app=app)
    if firebase_user.uid != firebase_uid:
        raise ValueError("Firebase returned a different UID")
    if firebase_user.disabled:
        raise ValueError("Firebase account is disabled")
    if firebase_user.email_verified is not True:
        raise ValueError("Firebase account email is not verified")
    return firebase_user


def apply_mapping(db, firebase_auth, app, row: dict[str, str], verified_by: str) -> str:
    # Confirm that this exact Firebase UID exists in the configured project. The
    # operator must verify ownership through reauthentication or another reviewed
    # proof; matching email addresses are never used as evidence.
    validate_firebase_account(firebase_auth, app, row["firebase_uid"])

    from app.models.identity_mapping import FirebaseIdentityMapping
    from app.models.user import User

    user = (
        db.query(User)
        .filter(User.legacy_auth_uid == row["legacy_auth_uid"])
        .with_for_update()
        .one_or_none()
    )
    if user is None:
        raise ValueError("No profile has the supplied legacy UID")

    audit = (
        db.query(FirebaseIdentityMapping)
        .filter(FirebaseIdentityMapping.legacy_auth_uid == row["legacy_auth_uid"])
        .one_or_none()
    )
    if user.firebase_uid == row["firebase_uid"]:
        if audit and audit.firebase_uid == row["firebase_uid"]:
            return "already_mapped"
        raise ValueError("Existing UID assignment has no matching audit record")
    if user.firebase_uid is not None:
        raise ValueError("Profile is already mapped to a different Firebase UID")
    if audit is not None:
        raise ValueError("Legacy UID is already present in the mapping audit table")

    existing_identity = (
        db.query(User)
        .filter(User.firebase_uid == row["firebase_uid"])
        .one_or_none()
    )
    if existing_identity is not None:
        raise ValueError("Firebase UID is already assigned to another profile")

    user.firebase_uid = row["firebase_uid"]
    db.add(
        FirebaseIdentityMapping(
            user_id=user.id,
            legacy_auth_uid=row["legacy_auth_uid"],
            firebase_uid=row["firebase_uid"],
            verified_by=verified_by,
            verification_method=row["verification_method"],
            evidence_ref=row["evidence_ref"],
        )
    )
    return "mapped"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True, type=Path, help="Owner-reviewed mapping CSV")
    parser.add_argument("--verified-by", required=True, help="Operator identity recorded in the audit table")
    parser.add_argument("--apply", action="store_true", help="Apply mappings after verification")
    args = parser.parse_args()
    if not args.verified_by.strip():
        parser.error("--verified-by must not be empty")

    try:
        rows = read_mappings(args.csv)
    except (OSError, ValueError) as exc:
        print(f"Mapping input rejected: {exc}", file=sys.stderr)
        return 2

    if not args.apply:
        print(f"Validated {len(rows)} mapping row(s); no database or Firebase service was contacted.")
        print("Review account ownership evidence, then rerun with --apply to write mappings.")
        return 0

    try:
        from app.core.security import get_firebase_admin_app
        from app.database.session import SessionLocal

        _, firebase_auth, app = get_firebase_admin_app()
    except Exception as exc:
        print(f"Firebase Admin is unavailable ({type(exc).__name__}); no mappings were applied.", file=sys.stderr)
        return 2

    counts = {"mapped": 0, "already_mapped": 0, "unresolved": 0}
    for row_number, row in enumerate(rows, start=2):
        db = SessionLocal()
        try:
            result = apply_mapping(db, firebase_auth, app, row, args.verified_by.strip())
            db.commit()
            counts[result] += 1
        except Exception as exc:
            db.rollback()
            counts["unresolved"] += 1
            print(
                f"CSV row {row_number} unresolved ({type(exc).__name__}); legacy data remains unchanged.",
                file=sys.stderr,
            )
        finally:
            db.close()

    print(
        "Mapping run complete: "
        f"{counts['mapped']} mapped, {counts['already_mapped']} already mapped, "
        f"{counts['unresolved']} unresolved. Unresolved profiles retain their legacy identifiers."
    )
    return 1 if counts["unresolved"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
