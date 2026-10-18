import hashlib
import hmac
import json
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.user import User
from app.schemas.payment import CheckoutRequest, TransactionResult

router = APIRouter(prefix="/payments", tags=["Payments"])
STRIPE_API = "https://api.stripe.com/v1"
WEBHOOK_TOLERANCE_SECONDS = 300


def _course_amount_cents(course: Course) -> int:
    return int((Decimal(str(course.price)) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _stripe_request(path: str, *, method: str, form: dict[str, Any] | None = None) -> dict[str, Any]:
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Payment provider is not configured")
    body = urllib.parse.urlencode(form).encode("utf-8") if form is not None else None
    request = urllib.request.Request(
        f"{STRIPE_API}/{path}",
        data=body,
        headers={
            "Authorization": f"Bearer {settings.STRIPE_SECRET_KEY}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=502, detail="Payment provider request failed") from exc


def _get_payment_intent(transaction_id: str) -> dict[str, Any]:
    if not transaction_id.startswith("pi_") or len(transaction_id) > 128:
        raise HTTPException(status_code=400, detail="Invalid payment transaction identifier")
    return _stripe_request(
        f"payment_intents/{urllib.parse.quote(transaction_id, safe='')}",
        method="GET",
    )


def _validate_payment_intent(
    intent: dict[str, Any], *, user_id: int, course: Course
) -> None:
    metadata = intent.get("metadata") or {}
    if str(metadata.get("user_id", "")) != str(user_id) or str(metadata.get("course_id", "")) != str(course.id):
        raise HTTPException(status_code=403, detail="Payment does not belong to this account and course")
    if intent.get("status") != "succeeded":
        raise HTTPException(status_code=402, detail="Payment has not completed")
    if (
        intent.get("currency") != "usd"
        or int(intent.get("amount_received") or 0) != _course_amount_cents(course)
    ):
        raise HTTPException(status_code=400, detail="Payment amount or currency does not match the course")


def _enroll_once(db: Session, *, user_id: int, course_id: int) -> None:
    existing = (
        db.query(Enrollment)
        .filter(Enrollment.user_id == user_id, Enrollment.course_id == course_id)
        .first()
    )
    if existing is None:
        db.add(Enrollment(user_id=user_id, course_id=course_id))
        try:
            db.commit()
        except Exception:
            db.rollback()
            # A concurrent successful webhook or verify request may have inserted it.
            existing = (
                db.query(Enrollment)
                .filter(Enrollment.user_id == user_id, Enrollment.course_id == course_id)
                .first()
            )
            if existing is None:
                raise


@router.post("/create", response_model=TransactionResult)
def create_payment(
    request: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = db.query(Course).filter(Course.id == request.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    existing = (
        db.query(Enrollment)
        .filter(Enrollment.user_id == current_user.id, Enrollment.course_id == course.id)
        .first()
    )
    if existing:
        return TransactionResult(transaction_id=f"already_enrolled_{course.id}", status="SUCCESS")

    if course.price <= 0:
        _enroll_once(db, user_id=current_user.id, course_id=course.id)
        return TransactionResult(transaction_id=f"free_enroll_{uuid.uuid4().hex[:12]}", status="SUCCESS")

    intent = _stripe_request(
        "payment_intents",
        method="POST",
        form={
            "amount": _course_amount_cents(course),
            "currency": "usd",
            "metadata[course_id]": course.id,
            "metadata[user_id]": current_user.id,
        },
    )
    intent_id = intent.get("id")
    if not isinstance(intent_id, str) or not intent_id.startswith("pi_"):
        raise HTTPException(status_code=502, detail="Payment provider returned an invalid transaction")
    return TransactionResult(
        transaction_id=intent_id,
        status="SUCCESS" if intent.get("status") == "succeeded" else "PENDING",
    )


@router.post("/verify", response_model=TransactionResult)
def verify_payment(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    intent = _get_payment_intent(transaction_id)
    if intent.get("id") != transaction_id:
        raise HTTPException(status_code=400, detail="Payment provider returned a mismatched transaction")
    metadata = intent.get("metadata") or {}
    if str(metadata.get("user_id", "")) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Payment does not belong to this account")

    try:
        course_id = int(metadata.get("course_id", ""))
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="Payment is missing a valid course reference") from exc
    course = db.query(Course).filter(Course.id == course_id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")

    _validate_payment_intent(intent, user_id=current_user.id, course=course)
    _enroll_once(db, user_id=current_user.id, course_id=course.id)
    return TransactionResult(transaction_id=transaction_id, status="SUCCESS")


def _verify_stripe_signature(payload: bytes, signature: str, secret: str) -> bool:
    fields: dict[str, list[str]] = {}
    for part in signature.split(","):
        key, separator, value = part.partition("=")
        if separator:
            fields.setdefault(key, []).append(value)
    timestamps = fields.get("t", [])
    signatures = fields.get("v1", [])
    if not timestamps or not signatures:
        return False
    try:
        timestamp = int(timestamps[0])
    except ValueError:
        return False
    if abs(int(time.time()) - timestamp) > WEBHOOK_TOLERANCE_SECONDS:
        return False

    signed_payload = str(timestamp).encode("ascii") + b"." + payload
    expected = hmac.new(secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()
    return any(hmac.compare_digest(expected, candidate) for candidate in signatures)


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="stripe-signature"),
    db: Session = Depends(get_db),
):
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="Payment webhook is not configured")
    payload = await request.body()
    if not stripe_signature or not _verify_stripe_signature(
        payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
    ):
        raise HTTPException(status_code=400, detail="Invalid payment webhook signature")

    try:
        event = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid payment webhook payload") from exc

    if event.get("type") == "payment_intent.succeeded":
        intent = (event.get("data") or {}).get("object") or {}
        metadata = intent.get("metadata") or {}
        try:
            user_id = int(metadata.get("user_id", ""))
            course_id = int(metadata.get("course_id", ""))
        except (TypeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail="Payment webhook has invalid ownership metadata") from exc
        user = db.query(User).filter(User.id == user_id).first()
        course = db.query(Course).filter(Course.id == course_id).first()
        if user is None or course is None:
            raise HTTPException(status_code=400, detail="Payment webhook references an unknown account or course")
        _validate_payment_intent(intent, user_id=user.id, course=course)
        _enroll_once(db, user_id=user.id, course_id=course.id)

    return {"received": True}
