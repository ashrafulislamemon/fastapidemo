from sqlalchemy import Column, Integer, String, Boolean, Date
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)  # ✅ length added
    email = Column(String(100), unique=True, index=True, nullable=False)    # ✅ length added
    password = Column(String(500), nullable=False)                          # ✅ hashed password may be long
    birthdate = Column(Date)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
