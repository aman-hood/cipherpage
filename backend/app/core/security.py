from typing import Any
import jwt
from jwt.exceptions import PyJWTError
from app.core.config import settings

def decode_supabase_token(token: str) -> dict[str, Any]:
    """
    Decodes the Supabase JWT.
    Note: Supabase JWTs use HS256 with the Supabase JWT Secret.
    """
    try:
        return jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated"
        )
    except PyJWTError as e:
        raise e
