from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.auth import UserProfile, UserProfileUpdate
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.core.security import FirebaseVerificationUnavailable, get_firebase_admin_app

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.get("/me", response_model=UserProfile)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Returns the current authenticated user's profile.
    Calling this endpoint safely provisions a profile from a verified Firebase identity.
    """
    return {
        "id": current_user.id,
        "firebase_uid": current_user.firebase_uid,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role
    }


@router.patch("/me", response_model=UserProfile)
def update_me(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the current user's app display name; identity and role stay server-controlled."""
    current_user.name = profile_update.name
    try:
        db.commit()
        db.refresh(current_user)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to save your profile right now",
        ) from exc

    return {
        "id": current_user.id,
        "firebase_uid": current_user.firebase_uid,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
    }


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user: User = Depends(get_current_user)):
    """Revoke Firebase refresh tokens; the client must also clear its local session."""
    try:
        _, firebase_auth, app = get_firebase_admin_app()
        firebase_auth.revoke_refresh_tokens(current_user.firebase_uid, app=app)
    except FirebaseVerificationUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is temporarily unavailable",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to revoke the authentication session",
        ) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
