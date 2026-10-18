from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import (
    FirebaseTokenInvalid,
    FirebaseVerificationUnavailable,
    verify_firebase_id_token,
)
from app.database.session import get_db
from app.models.user import User
from app.models.course import Course
from app.models.enrollment import Enrollment

bearer_scheme = HTTPBearer(auto_error=False)


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="A valid Firebase ID token is required",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _unauthorized()

    try:
        claims = verify_firebase_id_token(credentials.credentials)
    except FirebaseTokenInvalid as exc:
        raise _unauthorized() from exc
    except FirebaseVerificationUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is temporarily unavailable",
        ) from exc

    firebase_uid = claims.get("uid") or claims.get("sub")
    email = claims.get("email")
    if (
        not isinstance(firebase_uid, str)
        or not firebase_uid
        or not isinstance(email, str)
        or not email
        or claims.get("email_verified") is not True
    ):
        raise _unauthorized()

    email = email.strip().lower()
    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    if user is None:
        # Do not attach an unverified provider identity to an old profile merely
        # because its email string matches. Existing identities need an explicit,
        # audited mapping before the account can use its historical data.
        email_match = db.query(User).filter(func.lower(User.email) == email).first()
        if email_match is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This profile requires an administrator-reviewed identity mapping",
            )

        display_name = claims.get("name")
        if not isinstance(display_name, str) or not display_name.strip():
            display_name = email.split("@", 1)[0]
        user = User(
            firebase_uid=firebase_uid,
            email=email,
            name=display_name.strip(),
            role="STUDENT",
            is_active=True,
        )
        db.add(user)
        try:
            db.commit()
            db.refresh(user)
        except IntegrityError as exc:
            db.rollback()
            # Another request may have provisioned the same UID concurrently.
            user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A profile with this email already exists and needs identity review",
                ) from exc

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")
    return user


def require_student(user: User = Depends(get_current_user)) -> User:
    return user


def require_teacher(user: User = Depends(get_current_user)) -> User:
    if user.role not in {"TEACHER", "INSTRUCTOR", "ADMIN"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough privileges")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough privileges")
    return user


def ensure_course_access(db: Session, user: User, course: Course) -> None:
    """Require enrollment before exposing paid course resources to learners."""
    if user.role in {"ADMIN", "TEACHER", "INSTRUCTOR"} or course.price <= 0:
        return
    enrollment = (
        db.query(Enrollment)
        .filter(
            Enrollment.user_id == user.id,
            Enrollment.course_id == course.id,
            Enrollment.status.in_(["ACTIVE", "COMPLETED"]),
        )
        .first()
    )
    if enrollment is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="An active course enrollment is required to access this resource",
        )
