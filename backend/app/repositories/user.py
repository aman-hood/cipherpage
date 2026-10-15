from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.base import CRUDBase
from app.models.user import User
from app.schemas.auth import UserSync

class UserRepository(CRUDBase[User, UserSync, UserSync]):
    def get_by_supabase_id(self, db: Session, *, supabase_id: str) -> Optional[User]:
        return db.query(User).filter(User.supabase_user_id == supabase_id).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def create_with_supabase(self, db: Session, *, supabase_id: str, email: str, name: str) -> User:
        db_obj = User(
            supabase_user_id=supabase_id,
            email=email,
            name=name,
            role="STUDENT"
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

user_repo = UserRepository(User)
