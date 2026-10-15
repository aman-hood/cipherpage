from pydantic import BaseModel
from typing import Optional

class UserSync(BaseModel):
    name: Optional[str] = None
    email: str

class UserProfile(BaseModel):
    id: int
    supabase_user_id: str
    name: str
    email: str
    role: str
