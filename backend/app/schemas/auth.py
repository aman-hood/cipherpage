from pydantic import BaseModel, Field, field_validator


class UserProfile(BaseModel):
    id: int
    firebase_uid: str
    name: str
    email: str
    role: str


class UserProfileUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=120)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("Name cannot be blank")
        return normalized
