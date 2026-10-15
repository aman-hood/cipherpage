from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.dependencies.auth import require_admin
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/users", response_model=List[Dict[str, Any]])
def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """
    Retrieves paginated registered users. Strictly restricted to ADMIN role.
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return [
        {
            "id": u.id,
            "supabase_user_id": u.supabase_user_id,
            "email": u.email,
            "name": u.name,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat() if u.created_at else None
        }
        for u in users
    ]
