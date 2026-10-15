from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import PyJWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.database.session import get_db
from app.models.user import User
from app.core.security import decode_supabase_token

# We don't actually handle the login directly, but FastAPI's docs can use this URL for auth if needed.
# Typically we just send the Bearer token manually in the frontend.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception

    # Allow demo/dev token only if explicitly permitted in development environment
    if settings.ENVIRONMENT == "development" and settings.ALLOW_DEV_TOKENS:
        if token in ["demo-token", "dev-token"]:
            demo_user = db.query(User).filter(User.email == "demo@cipherpage.com").first()
            if demo_user:
                return demo_user

    try:
        payload = decode_supabase_token(token)
        supabase_user_id: str = payload.get("sub")
        email: str = payload.get("email")
        # Supabase stores extra meta in user_metadata
        user_metadata = payload.get("user_metadata", {})
        name: str = user_metadata.get("name", email.split("@")[0] if email else "User")
        
        if supabase_user_id is None or email is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception

    # Auto-sync user if they do not exist with race condition protection
    user = db.query(User).filter(User.supabase_user_id == supabase_user_id).first()
    if user is None:
        try:
            user = User(
                supabase_user_id=supabase_user_id,
                email=email,
                name=name,
                role="STUDENT"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        except Exception:
            db.rollback()
            user = db.query(User).filter(User.supabase_user_id == supabase_user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error synchronizing user profile"
                )

    return user

def require_student(user: User = Depends(get_current_user)) -> User:
    return user

def require_teacher(user: User = Depends(get_current_user)) -> User:
    if user.role not in ["TEACHER", "ADMIN"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough privileges")
    return user

def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough privileges")
    return user
