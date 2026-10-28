from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from app.schemas.role import RoleRead


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    full_name: str
    role_id: int
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(min_length=8, description="Plain text password, hashed before persistence")


class UserRead(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    role: Optional[RoleRead] = None

    model_config = ConfigDict(from_attributes=True)
