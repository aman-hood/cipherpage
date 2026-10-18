"""Firebase ID token verification using the trusted Firebase Admin SDK."""

from typing import Any
import json

from app.core.config import settings


class FirebaseVerificationUnavailable(RuntimeError):
    """Firebase verification cannot run because server configuration is unavailable."""


class FirebaseTokenInvalid(ValueError):
    """The supplied Firebase ID token is invalid, expired, or revoked."""


def get_firebase_admin_app():
    if not settings.FIREBASE_PROJECT_ID:
        raise FirebaseVerificationUnavailable("Firebase project is not configured")

    try:
        import firebase_admin
        from firebase_admin import auth, credentials
    except ImportError as exc:
        raise FirebaseVerificationUnavailable("Firebase Admin SDK is not installed") from exc

    try:
        try:
            app = firebase_admin.get_app()
        except ValueError:
            service_account = settings.FIREBASE_SERVICE_ACCOUNT_JSON
            credential = (
                credentials.Certificate(json.loads(service_account))
                if service_account
                else credentials.ApplicationDefault()
            )
            app = firebase_admin.initialize_app(
                credential,
                {"projectId": settings.FIREBASE_PROJECT_ID},
            )
    except Exception as exc:
        raise FirebaseVerificationUnavailable("Firebase Admin credentials are unavailable") from exc
    if getattr(app, "project_id", None) != settings.FIREBASE_PROJECT_ID:
        raise FirebaseVerificationUnavailable("Firebase Admin app targets a different project")
    return firebase_admin, auth, app


def verify_firebase_id_token(token: str) -> dict[str, Any]:
    _, auth, app = get_firebase_admin_app()

    try:
        claims = auth.verify_id_token(
            token,
            app=app,
            check_revoked=settings.FIREBASE_CHECK_REVOKED,
        )
    except (
        auth.InvalidIdTokenError,
        auth.ExpiredIdTokenError,
        auth.RevokedIdTokenError,
        auth.UserDisabledError,
        auth.UserNotFoundError,
        ValueError,
    ) as exc:
        raise FirebaseTokenInvalid("Firebase ID token is invalid") from exc
    except Exception as exc:
        # Certificate fetches and Firebase outages are service availability failures,
        # not evidence that a user's credentials were invalid.
        raise FirebaseVerificationUnavailable("Firebase token verification is unavailable") from exc

    if claims.get("aud") != settings.FIREBASE_PROJECT_ID:
        raise FirebaseTokenInvalid("Firebase ID token has an unexpected audience")
    return claims
