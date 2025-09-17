from sqlalchemy import Column, Integer, String, Boolean, Date, Enum, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import enum

# -----------------
# Role
# -----------------
class UserRole(str, enum.Enum):
    superadmin = "superadmin"
    admin = "admin"
    manager = "manager"
    user = "user"

# -----------------
# Users
# -----------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    birthdate = Column(Date)
    role = Column(Enum(UserRole), default=UserRole.user)
    is_active = Column(Boolean, default=True)
    
    groups = relationship("Group", secondary="user_group_link", back_populates="users")

# -----------------
# Groups
# -----------------
class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    
    users = relationship("User", secondary="user_group_link", back_populates="groups")

# -----------------
# Many-to-Many link
# -----------------
user_group_link = Table(
    "user_group_link",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("group_id", Integer, ForeignKey("groups.id"))
)

# -----------------
# Tasks
# -----------------
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    description = Column(String(500))
    assigned_group_id = Column(Integer, ForeignKey("groups.id"))
    status = Column(String(50), default="pending")
