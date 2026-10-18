from pydantic import BaseModel
class UserProfile(BaseModel):
    id: int
    firebase_uid: str
    name: str
    email: str
    role: str
