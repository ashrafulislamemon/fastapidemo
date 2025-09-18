from pydantic import BaseModel
from typing import List,Optional
from enum import Enum
from datetime import date

class UserRole(str, Enum):
    superadmin = "superadmin"
    admin = "admin"
    manager = "manager"
    user = "user"

# Base schema শুধু “input হিসেবে user থেকে কি field নিতে হবে” তা define করে।

# তাই যদি Base-এ শুধু name থাকে → client শুধু name পাঠাবে।

class GroupBase(BaseModel):
    name: str

# Group Response ta Groupbase inherit kore mane group class er ki ase and ekhane ki disi seta soho response kore    
# যেহেতু users: List[str] = [] লেখা আছে, তাই multiple users থাকলে সব দেখাবে।

# আর যদি কোনো user না থাকে, empty list [] হিসেবে response যাবে।

# from_attributes=True + Pydantic schema use করলে, FastAPI response-এ data JSON আকারে যাবে।
class GroupResponse(GroupBase):
    id: int
    users: List[str] = []
    model_config = {"from_attributes": True}

class UserBase(BaseModel):
    username: str
    email: str
    birthdate: date


# Create schema = API input validation এর জন্য।

# এখানে তুমি শুধু সেই fields দিবে যেগুলো user দিতে পারে / validate করতে চাও।

# Extra fields যেমন database-generated বা ORM fields (id, created_at, nested relations) Create schema-এ লাগবে না, তারা Response schema-এ থাকবে।


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

    # model_config = {"from_attributes": True} (v2)   class config(v1) ar model_config same e kaj kore just likha alada

class PermissionBase(BaseModel):
    name: str

class PermissionResponse(PermissionBase):
    id: int
    model_config = {"from_attributes": True}

class RoleBase(BaseModel):
    name: str

class RoleResponse(RoleBase):
    id: int
    permissions: List[PermissionResponse] = []
    model_config = {"from_attributes": True}    