import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.modules.users.models import Role


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    is_active: bool
    role: Role


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
