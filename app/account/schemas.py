from pydantic import BaseModel
from datetime import date

class UserBase(BaseModel):
    username: str
    email: str
    birthdate: date

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_superuser: bool

    model_config = {"from_attributes": True}  # Pydantic v2

class Token(BaseModel):
    access_token: str
    token_type: str
