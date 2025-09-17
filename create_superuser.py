import os
from dotenv import load_dotenv
from app.database import SessionLocal
from app.account import models
from app.core.security import hash_password
from datetime import date

load_dotenv()

def create_superuser():
    db = SessionLocal()
    username = os.getenv("ADMIN_USERNAME")
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")

    if db.query(models.User).filter(models.User.username==username).first():
        print("Superuser already exists")
        return

    admin = models.User(
        username=username,
        email=email,
        password=hash_password(password),
        birthdate=date.today(),
        role=models.UserRole.superadmin
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    print("Superuser created:", admin.username)

if __name__ == "__main__":
    create_superuser()
