import hashlib
import hmac
import sys
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from firebase_admin import auth as firebase_auth

from app.core import security
from app.core.config import Settings
from app.core.security import FirebaseTokenInvalid, FirebaseVerificationUnavailable
from app.dependencies import auth as auth_dependencies
from app.models.course import Course, Lecture
from app.models.enrollment import Enrollment
from app.models.user import User
from app.dependencies.auth import ensure_course_access
from app.repositories.progress import progress_repo
from app.routers import ai as ai_router
from app.routers import payments
from app.schemas.rag import DocumentIngestRequest, RAGQueryRequest
from app.schemas.progress import ProgressUpdate
from app.services.enrollment import enrollment_service
from app.services.progress import progress_service
from app.services import rag_assistant

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.migrate_firebase_identities import read_mappings, validate_firebase_account


class FakeQuery:
    def __init__(self, first=None, all_rows=None):
        self.first_result = first
        self.all_result = all_rows or []
        self.filters = []

    def filter(self, *args, **kwargs):
        self.filters.extend(args)
        return self

    def order_by(self, *args, **kwargs):
        return self

    def first(self):
        return self.first_result

    def all(self):
        return self.all_result


class FakeDatabase:
    def __init__(self, query_results=None):
        self.query_results = query_results or {}
        self.added = []
        self.commits = 0
        self.rollbacks = 0
        self.queries = []

    def query(self, model):
        values = self.query_results.get(model)
        if values is None:
            value = None
        else:
            value = values.pop(0) if isinstance(values, list) else values
        if isinstance(value, FakeQuery):
            query = value
        elif isinstance(value, list):
            query = FakeQuery(all_rows=value)
        else:
            query = FakeQuery(first=value)
        self.queries.append((model, query))
        return query

    def add(self, row):
        self.added.append(row)

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def refresh(self, row):
        row.id = 42

    def flush(self):
        pass


def bearer():
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials="test-id-token")


class FirebaseAuthenticationRegressionTests(unittest.TestCase):
    @patch.object(firebase_auth, "verify_id_token", side_effect=firebase_auth.InvalidIdTokenError("invalid"))
    @patch.object(security, "get_firebase_admin_app", return_value=(None, firebase_auth, object()))
    def test_firebase_admin_invalid_token_exception_is_mapped(self, _app, _verify):
        with self.assertRaises(FirebaseTokenInvalid):
            security.verify_firebase_id_token("bad-token")


class FirebaseIdentityMigrationRegressionTests(unittest.TestCase):
    def test_identity_import_rejects_unverified_firebase_account(self):
        firebase_auth = SimpleNamespace(
            get_user=lambda uid, app: SimpleNamespace(
                uid=uid, disabled=False, email_verified=False
            )
        )
        with self.assertRaisesRegex(ValueError, "email is not verified"):
            validate_firebase_account(firebase_auth, object(), "firebase-user-1")

    def test_identity_import_rejects_disabled_firebase_account(self):
        firebase_auth = SimpleNamespace(
            get_user=lambda uid, app: SimpleNamespace(
                uid=uid, disabled=True, email_verified=True
            )
        )
        with self.assertRaisesRegex(ValueError, "account is disabled"):
            validate_firebase_account(firebase_auth, object(), "firebase-user-1")

    def test_identity_csv_dry_run_rejects_duplicate_uids(self):
        content = (
            "legacy_auth_uid,firebase_uid,verification_method,evidence_ref\n"
            "legacy-1,firebase-1,reauthenticated,case-1\n"
            "legacy-2,firebase-1,reauthenticated,case-2\n"
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "mappings.csv"
            path.write_text(content, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate legacy or Firebase UIDs"):
                read_mappings(path)


class RemoteConfigurationSecurityTests(unittest.TestCase):
    def test_remote_database_urls_require_tls(self):
        settings = Settings(DATABASE_URL="postgresql://app:secret@neon.example.invalid/db")
        self.assertEqual(settings.sqlalchemy_database_url().query["sslmode"], "require")

    def test_remote_database_urls_reject_disabled_tls(self):
        settings = Settings(
            DATABASE_URL="postgresql://app:secret@neon.example.invalid/db?sslmode=disable"
        )
        with self.assertRaises(ValueError):
            settings.sqlalchemy_database_url()

    def test_remote_cors_requires_exact_https_origins(self):
        with self.assertRaises(ValueError):
            Settings(
                DATABASE_URL="postgresql://app:secret@neon.example.invalid/db",
                ENVIRONMENT="production",
                ALLOWED_ORIGINS="http://localhost:3000",
            )
        settings = Settings(
            DATABASE_URL="postgresql://app:secret@neon.example.invalid/db",
            ENVIRONMENT="production",
            ALLOWED_ORIGINS="https://app.example.invalid",
        )
        self.assertEqual(settings.cors_origins, ["https://app.example.invalid"])

    @patch.object(auth_dependencies, "verify_firebase_id_token")
    def test_missing_token_is_rejected(self, verify):
        with self.assertRaises(HTTPException) as raised:
            auth_dependencies.get_current_user(db=FakeDatabase(), credentials=None)
        self.assertEqual(raised.exception.status_code, 401)
        verify.assert_not_called()

    @patch.object(auth_dependencies, "verify_firebase_id_token", side_effect=FirebaseTokenInvalid())
    def test_invalid_or_expired_token_is_rejected(self, _verify):
        with self.assertRaises(HTTPException) as raised:
            auth_dependencies.get_current_user(db=FakeDatabase(), credentials=bearer())
        self.assertEqual(raised.exception.status_code, 401)

    @patch.object(auth_dependencies, "verify_firebase_id_token", side_effect=FirebaseVerificationUnavailable())
    def test_firebase_outage_is_not_misreported_as_invalid_credentials(self, _verify):
        with self.assertRaises(HTTPException) as raised:
            auth_dependencies.get_current_user(db=FakeDatabase(), credentials=bearer())
        self.assertEqual(raised.exception.status_code, 503)

    @patch.object(auth_dependencies, "verify_firebase_id_token", return_value={
        "uid": "firebase-user-1",
        "email": "new@example.invalid",
        "email_verified": False,
    })
    def test_unverified_email_is_rejected_before_profile_provisioning(self, _verify):
        db = FakeDatabase()
        with self.assertRaises(HTTPException) as raised:
            auth_dependencies.get_current_user(db=db, credentials=bearer())
        self.assertEqual(raised.exception.status_code, 401)
        self.assertEqual(db.added, [])

    @patch.object(auth_dependencies, "verify_firebase_id_token", return_value={
        "uid": "firebase-user-1",
        "sub": "firebase-user-1",
        "email": "new@example.invalid",
        "email_verified": True,
        "name": "New Learner",
        "role": "ADMIN",
    })
    def test_new_profile_ignores_client_role_claim_and_defaults_to_student(self, _verify):
        db = FakeDatabase({User: [None, None]})
        profile = auth_dependencies.get_current_user(db=db, credentials=bearer())
        self.assertEqual(profile.firebase_uid, "firebase-user-1")
        self.assertEqual(profile.role, "STUDENT")
        self.assertEqual(db.commits, 1)

    @patch.object(auth_dependencies, "verify_firebase_id_token", return_value={
        "uid": "different-firebase-user",
        "email": "legacy@example.invalid",
        "email_verified": True,
    })
    def test_matching_email_does_not_auto_link_legacy_profile(self, _verify):
        legacy = SimpleNamespace(firebase_uid=None, legacy_auth_uid="legacy-1")
        db = FakeDatabase({User: [None, legacy]})
        with self.assertRaises(HTTPException) as raised:
            auth_dependencies.get_current_user(db=db, credentials=bearer())
        self.assertEqual(raised.exception.status_code, 409)
        self.assertEqual(db.added, [])

    @patch.object(auth_dependencies, "verify_firebase_id_token", return_value={
        "uid": "disabled-user",
        "email": "disabled@example.invalid",
        "email_verified": True,
    })
    def test_inactive_application_profile_is_forbidden(self, _verify):
        inactive = SimpleNamespace(is_active=False)
        db = FakeDatabase({User: [inactive]})
        with self.assertRaises(HTTPException) as raised:
            auth_dependencies.get_current_user(db=db, credentials=bearer())
        self.assertEqual(raised.exception.status_code, 403)


class PaymentRegressionTests(unittest.TestCase):
    def setUp(self):
        self.user = SimpleNamespace(id=7)
        self.course = SimpleNamespace(id=9, price=12.50)

    def test_fabricated_legacy_style_transaction_id_is_rejected(self):
        with self.assertRaises(HTTPException) as raised:
            payments._get_payment_intent("txn_7_9_123456")
        self.assertEqual(raised.exception.status_code, 400)

    @patch.object(payments, "_get_payment_intent", return_value={
        "id": "pi_pending",
        "status": "requires_payment_method",
        "amount_received": 0,
        "currency": "usd",
        "metadata": {"user_id": "7", "course_id": "9"},
    })
    def test_pending_provider_transaction_cannot_enroll(self, _get_intent):
        db = FakeDatabase({Course: [self.course]})
        with self.assertRaises(HTTPException) as raised:
            payments.verify_payment("pi_pending", db=db, current_user=self.user)
        self.assertEqual(raised.exception.status_code, 402)
        self.assertEqual(db.added, [])
        self.assertEqual(db.commits, 0)

    @patch.object(payments, "_get_payment_intent", return_value={
        "id": "pi_succeeded",
        "status": "succeeded",
        "amount_received": 1250,
        "currency": "usd",
        "metadata": {"user_id": "8", "course_id": "9"},
    })
    def test_other_users_payment_cannot_enroll_current_user(self, _get_intent):
        db = FakeDatabase({Course: [self.course]})
        with self.assertRaises(HTTPException) as raised:
            payments.verify_payment("pi_succeeded", db=db, current_user=self.user)
        self.assertEqual(raised.exception.status_code, 403)
        self.assertEqual(db.added, [])

    @patch.object(payments, "_get_payment_intent", return_value={
        "id": "pi_succeeded",
        "status": "succeeded",
        "amount_received": 1250,
        "currency": "usd",
        "metadata": {"user_id": "7", "course_id": "9"},
    })
    def test_verified_paid_transaction_creates_enrollment(self, _get_intent):
        db = FakeDatabase({Course: [self.course], Enrollment: [None]})
        result = payments.verify_payment("pi_succeeded", db=db, current_user=self.user)
        self.assertEqual(result.status, "SUCCESS")
        self.assertEqual(len(db.added), 1)
        self.assertEqual(db.added[0].user_id, 7)
        self.assertEqual(db.added[0].course_id, 9)

    def test_webhook_signature_requires_fresh_timestamp_and_matching_hmac(self):
        timestamp = int(time.time())
        payload = b'{"type":"payment_intent.succeeded"}'
        secret = "unit-test-secret"
        signature = hmac.new(secret.encode(), str(timestamp).encode() + b"." + payload, hashlib.sha256).hexdigest()
        header = f"t={timestamp},v1={signature}"
        self.assertTrue(payments._verify_stripe_signature(payload, header, secret))
        self.assertFalse(payments._verify_stripe_signature(payload, header, "wrong-secret"))
        self.assertFalse(payments._verify_stripe_signature(payload, f"t={timestamp - 1000},v1={signature}", secret))


class CourseAuthorizationRegressionTests(unittest.TestCase):
    def test_unenrolled_learner_cannot_access_paid_course_resource(self):
        student = SimpleNamespace(id=7, role="STUDENT")
        paid_course = SimpleNamespace(id=9, price=25.0)
        db = FakeDatabase({Enrollment: [None]})
        with self.assertRaises(HTTPException) as raised:
            ensure_course_access(db, student, paid_course)
        self.assertEqual(raised.exception.status_code, 403)

    @patch("app.services.enrollment.course_repo.get")
    @patch("app.services.enrollment.enrollment_repo.get_by_user_and_course", return_value=None)
    def test_direct_enrollment_cannot_bypass_paid_checkout(self, _existing, course_get):
        course_get.return_value = SimpleNamespace(id=9, price=25.0)
        student = SimpleNamespace(id=7)
        with self.assertRaises(HTTPException) as raised:
            enrollment_service.enroll_user(FakeDatabase(), course_id=9, user=student)
        self.assertEqual(raised.exception.status_code, 402)

    @patch.object(progress_repo, "get_lecture_progress")
    @patch.object(progress_repo, "get_user_stats")
    def test_uncompleting_and_recompleting_lecture_does_not_award_xp_twice(
        self, get_stats, get_lecture_progress
    ):
        from datetime import datetime

        course = SimpleNamespace(id=9, price=0.0)
        lecture = SimpleNamespace(id=3, module=SimpleNamespace(course=course))
        progress = SimpleNamespace(
            completed=False,
                completed_at=datetime.now(),
            watch_time_seconds=10,
        )
        stats = SimpleNamespace(total_xp=50, level=1)
        get_lecture_progress.return_value = progress
        get_stats.return_value = stats
        db = FakeDatabase({Lecture: [lecture]})

        progress_service.update_lecture_progress(
            db,
            user=SimpleNamespace(id=7, role="STUDENT"),
            update=ProgressUpdate(lecture_id=3, completed=True),
        )

        self.assertEqual(stats.total_xp, 50)
        self.assertTrue(progress.completed)


class DocumentAndRAGRegressionTests(unittest.TestCase):
    def test_document_listing_scopes_students_to_public_and_enrolled_courses(self):
        db = FakeDatabase({Enrollment.course_id: FakeQuery(all_rows=[(17,)])})
        user = SimpleNamespace(id=7, role="STUDENT")

        documents = ai_router.list_documents(db=db, current_user=user)

        self.assertEqual(documents, [])
        document_query = db.queries[0][1]
        visibility_filter = next(
            expression
            for expression in document_query.filters
            if " IS NULL" in str(expression) and " IN " in str(expression)
        )
        self.assertIn("documents.course_id IS NULL", str(visibility_filter))
        self.assertIn("documents.course_id IN", str(visibility_filter))

    def test_document_listing_rejects_unenrolled_course_filter(self):
        db = FakeDatabase({Enrollment.course_id: FakeQuery(all_rows=[(17,)])})
        user = SimpleNamespace(id=7, role="STUDENT")

        with self.assertRaises(HTTPException) as raised:
            ai_router.list_documents(course_id=99, db=db, current_user=user)

        self.assertEqual(raised.exception.status_code, 403)

    @patch.object(rag_assistant.vector_store, "search_similar_chunks", return_value=[])
    def test_rag_uses_active_and_completed_course_enrollments(self, search):
        db = FakeDatabase({Enrollment.course_id: FakeQuery(all_rows=[(17,)])})
        user = SimpleNamespace(id=7, role="STUDENT")

        rag_assistant.rag_service.answer_question(
            db=db,
            user=user,
            req=RAGQueryRequest(question="Explain course notes"),
        )

        self.assertEqual(search.call_args.kwargs["allowed_course_ids"], [17])
        enrollment_filters = [str(item) for item in db.queries[0][1].filters]
        self.assertTrue(any("enrollments.status IN" in item for item in enrollment_filters))

    @patch.object(
        rag_assistant.chunker,
        "chunk_text",
        side_effect=RuntimeError("private provider response"),
    )
    def test_document_ingestion_hides_provider_exception_details(self, _chunk):
        db = FakeDatabase()
        user = SimpleNamespace(id=7)
        request = DocumentIngestRequest(
            title="Private notes",
            course_id=17,
            content="Course material",
        )

        with self.assertRaises(HTTPException) as raised:
            rag_assistant.rag_service.ingest_document(db, user, request)

        self.assertEqual(raised.exception.status_code, 500)
        self.assertEqual(raised.exception.detail, "Document ingestion failed")
        self.assertNotIn("private provider response", str(raised.exception.detail))


if __name__ == "__main__":
    unittest.main()
