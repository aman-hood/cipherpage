from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.auth import UserProfile
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.get("/me", response_model=UserProfile)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Returns the current authenticated user's profile.
    Calling this endpoint also automatically syncs the Supabase user to the local database.
    """
    return {
        "id": current_user.id,
        "supabase_user_id": current_user.supabase_user_id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role
    }
