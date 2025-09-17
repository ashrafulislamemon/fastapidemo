from pydantic import BaseModel
from typing import List,Optional
from enum import Enum
from datetime import date

class UserRole(str, Enum):
    superadmin = "superadmin"
    admin = "admin"
    manager = "manager"
    user = "user"

class GroupBase(BaseModel):
    name: str

class GroupResponse(GroupBase):
    id: int
    users: List[str] = []
    model_config = {"from_attributes": True}

class UserBase(BaseModel):
    username: str
    email: str
    birthdate: date

class UserCreate(UserBase):
    password: str
    # role: UserRole = UserRole.user

class UserResponse(UserBase):
    id: int
    role: UserRole
    groups: List[GroupResponse] = []
    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str




class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_group_id: Optional[int] = None  # কোনো group assign করতে চাইলে

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: int
    status: str
    class Config:
        from_attributes = True
        