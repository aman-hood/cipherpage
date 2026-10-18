from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.base import CRUDBase
from app.models.user import User
from app.schemas.auth import UserProfile

class UserRepository(CRUDBase[User, UserProfile, UserProfile]):
    def get_by_firebase_uid(self, db: Session, *, firebase_uid: str) -> Optional[User]:
        return db.query(User).filter(User.firebase_uid == firebase_uid).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def create_with_firebase(self, db: Session, *, firebase_uid: str, email: str, name: str) -> User:
        db_obj = User(
            firebase_uid=firebase_uid,
            email=email,
            name=name,
            role="STUDENT"
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

user_repo = UserRepository(User)
