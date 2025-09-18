# from fastapi import APIRouter, Depends, HTTPException
# from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
# from sqlalchemy.orm import Session
# from datetime import timedelta
# from typing import Optional

# from app.database import get_db
# from app.account import models, schemas
# from app.core.security import (
#     hash_password,
#     verify_password,
#     create_access_token,
#     decode_access_token,
#     ACCESS_TOKEN_EXPIRE_MINUTES,
# )

# router = APIRouter()
# blacklist_tokens = set()
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/account/login")

# # -----------------------
# # CRUD helpers
# # -----------------------
# def get_user_by_username(db: Session, username: str):
#     return db.query(models.User).filter(models.User.username == username).first()
# def create_user(db: Session, user: schemas.UserCreate, is_superadmin: bool = False):
#     db_user = models.User(
#         username=user.username,
#         email=user.email,
#         password=hash_password(user.password),
#         birthdate=getattr(user, "birthdate", None),
#         role=models.UserRole.user,  # always default "user"
#     )
#     if is_superadmin:
#         db_user.role = models.UserRole.superadmin
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user


# def authenticate_user(db: Session, username: str, password: str):
#     user = get_user_by_username(db, username)
#     if not user or not verify_password(password, user.password):
#         return None
#     return user

# # -----------------------
# # Dependencies
# # -----------------------
# def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     if token in blacklist_tokens:
#         raise HTTPException(status_code=401, detail="Token revoked")
#     payload = decode_access_token(token)
#     if payload is None or "sub" not in payload:
#         raise HTTPException(status_code=401, detail="Invalid token")
#     username = payload.get("sub")
#     user = get_user_by_username(db, username)
#     if user is None:
#         raise HTTPException(status_code=401, detail="User not found")
#     return user

# def role_required(*roles: models.UserRole):
#     def dependency(current_user: models.User = Depends(get_current_user)):
#         if current_user.role not in roles:
#             raise HTTPException(status_code=403, detail="Access denied for your role")
#         return current_user
#     return dependency

# def superadmin_required(current_user: models.User = Depends(get_current_user)):
#     if current_user.role != models.UserRole.superadmin:
#         raise HTTPException(status_code=403, detail="Superadmin required")
#     return current_user

# # -----------------------
# # Auth Routes
# # -----------------------
# @router.post("/register", response_model=schemas.UserResponse)
# def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     if get_user_by_username(db, user.username):
#         raise HTTPException(status_code=400, detail="Username already exists")
#     return create_user(db, user, is_superadmin=False)

# @router.post("/login", response_model=schemas.Token)
# def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#     user = authenticate_user(db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     access_token = create_access_token(
#         data={"sub": user.username},
#         expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
#     )
#     return {"access_token": access_token, "token_type": "bearer"}

# @router.post("/logout")
# def logout(token: str = Depends(oauth2_scheme)):
#     blacklist_tokens.add(token)
#     return {"msg": "Logged out successfully"}

# # -----------------------
# # Group & User Management (Superadmin Only)
# # -----------------------
# @router.post("/groups", response_model=schemas.GroupResponse)
# def create_group(
#     group: schemas.GroupBase,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(superadmin_required),
# ):
#     existing_group = db.query(models.Group).filter(models.Group.name == group.name).first()
#     if existing_group:
#         raise HTTPException(status_code=400, detail="Group already exists")
#     db_group = models.Group(name=group.name)
#     db.add(db_group)
#     db.commit()
#     db.refresh(db_group)
#     return db_group

# @router.post("/groups/{group_id}/assign/{user_id}")
# def assign_user_to_group(
#     group_id: int,
#     user_id: int,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(superadmin_required),
# ):
#     group = db.query(models.Group).filter(models.Group.id == group_id).first()
#     user = db.query(models.User).filter(models.User.id == user_id).first()
#     if not group or not user:
#         raise HTTPException(status_code=404, detail="User or Group not found")
#     if user in group.users:
#         raise HTTPException(status_code=400, detail="User already in group")
#     group.users.append(user)
#     db.commit()
#     return {"msg": f"User {user.username} added to group {group.name}"}



# # task

# # -----------------------
# # Task Routes (Superadmin only)
# # -----------------------
# @router.post("/tasks", response_model=schemas.TaskResponse)
# def create_task(
#     task: schemas.TaskCreate,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(superadmin_required)
# ):
#     db_task = models.Task(
#         title=task.title,
#         description=task.description,
#         assigned_group_id=task.assigned_group_id
#     )
#     db.add(db_task)
#     db.commit()
#     db.refresh(db_task)
#     return db_task

# @router.get("/tasks", response_model=list[schemas.TaskResponse])
# def list_tasks(
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(superadmin_required)
# ):
#     return db.query(models.Task).all()

# @router.put("/tasks/{task_id}", response_model=schemas.TaskResponse)
# def update_task(
#     task_id: int,
#     task: schemas.TaskCreate,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(superadmin_required)
# ):
#     db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
#     if not db_task:
#         raise HTTPException(status_code=404, detail="Task not found")
#     db_task.title = task.title
#     db_task.description = task.description
#     db_task.assigned_group_id = task.assigned_group_id
#     db.commit()
#     db.refresh(db_task)
#     return db_task



# @router.put("/users/{user_id}/role")
# def update_user_role(
#     user_id: int,
#     new_role: models.UserRole,   # admin, manager, user
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(superadmin_required),  # শুধু superadmin পারবে
# ):
#     user = db.query(models.User).filter(models.User.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     # নিজের role পরিবর্তন আটকাতে চাইলে
#     if user.id == current_user.id:
#         raise HTTPException(status_code=400, detail="You cannot change your own role")

#     user.role = new_role
#     db.commit()
#     db.refresh(user)
#     return {"msg": f"User {user.username} promoted to {new_role}"}



# from fastapi import Depends, HTTPException
# from app.account import models
# from app.routes.auth import get_current_user

# def role_required(*allowed_roles: models.UserRole):
#     """
#     Route এ pass করা roles access পাবে।
#     কিন্তু সবসময় superadmin access পাবে।
#     """
#     def dependency(current_user: models.User = Depends(get_current_user)):
#         if current_user.role == models.UserRole.superadmin:
#             return current_user  # superadmin সবসময় allowed
#         if current_user.role not in allowed_roles:
#             raise HTTPException(status_code=403, detail="Access denied for your role")
#         return current_user
#     return dependency

# from fastapi import APIRouter, Depends
# from app.account import models, schemas
# from sqlalchemy.orm import Session
# from app.database import get_db

# router = APIRouter()

# # শুধু admin access দিবে, কিন্তু superadmin সবসময় allowed
# @router.post("/tasks", response_model=schemas.TaskResponse)
# def create_task(
#     task: schemas.TaskCreate,
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(role_required(models.UserRole.admin))
# ):
#     db_task = models.Task(
#         title=task.title,
#         description=task.description,
#         assigned_group_id=task.assigned_group_id
#     )
#     db.add(db_task)
#     db.commit()
#     db.refresh(db_task)
#     return db_task



# multiple hole  role_required(
#             models.UserRole.admin, 
#             models.UserRole.manager
#         )


from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional

from app.database import get_db
from app.account import models, schemas
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter()
blacklist_tokens = set()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/account/login")

# -----------------------
# CRUD helpers
# -----------------------
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate, is_superadmin: bool = False):
    db_user = models.User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password),
        birthdate=getattr(user, "birthdate", None),
        role=models.UserRole.user,  # default user
    )
    if is_superadmin:
        db_user.role = models.UserRole.superadmin
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.password):
        return None
    return user

# -----------------------
# Dependencies
# -----------------------
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if token in blacklist_tokens:
        raise HTTPException(status_code=401, detail="Token revoked")
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    username = payload.get("sub")
    user = get_user_by_username(db, username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Role check
def role_required(*roles: models.UserRole):
    def dependency(current_user: models.User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Access denied for your role")
        return current_user
    return dependency

# Superadmin only
def superadmin_required(current_user: models.User = Depends(get_current_user)):
    if current_user.role != models.UserRole.superadmin:
        raise HTTPException(status_code=403, detail="Superadmin required")
    return current_user

# Permission check
def permission_required(permission_name: str):
    def dependency(
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        role = db.query(models.Role).filter(models.Role.name == current_user.role.value).first()
        if not role:
            raise HTTPException(status_code=403, detail="Role not found")
        if not any(p.name == permission_name for p in role.permissions):
            raise HTTPException(status_code=403, detail=f"Permission '{permission_name}' required")
        return current_user
    return dependency

# -----------------------
# Auth Routes
# -----------------------
@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    return create_user(db, user, is_superadmin=False)

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout(token: str = Depends(oauth2_scheme)):
    blacklist_tokens.add(token)
    return {"msg": "Logged out successfully"}

# -----------------------
# Group & User Management
# -----------------------
@router.post("/groups", response_model=schemas.GroupResponse)
def create_group(
    group: schemas.GroupBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(permission_required("create_group")),
):
    existing_group = db.query(models.Group).filter(models.Group.name == group.name).first()
    if existing_group:
        raise HTTPException(status_code=400, detail="Group already exists")
    db_group = models.Group(name=group.name)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

@router.post("/groups/{group_id}/assign/{user_id}")
def assign_user_to_group(
    group_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(permission_required("assign_user")),
):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not group or not user:
        raise HTTPException(status_code=404, detail="User or Group not found")
    if user in group.users:
        raise HTTPException(status_code=400, detail="User already in group")
    group.users.append(user)
    db.commit()
    return {"msg": f"User {user.username} added to group {group.name}"}

# -----------------------
# Task Routes
# -----------------------
@router.post("/tasks", response_model=schemas.TaskResponse)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(permission_required("create_task"))
):
    db_task = models.Task(
        title=task.title,
        description=task.description,
        assigned_group_id=task.assigned_group_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/tasks", response_model=list[schemas.TaskResponse])
def list_tasks(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(permission_required("view_task"))
):
    return db.query(models.Task).all()

@router.put("/tasks/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: int,
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(permission_required("update_task"))
):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db_task.title = task.title
    db_task.description = task.description
    db_task.assigned_group_id = task.assigned_group_id
    db.commit()
    db.refresh(db_task)
    return db_task

# -----------------------
# User Role Management
# -----------------------
@router.put("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    new_role: models.UserRole,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(permission_required("change_role")),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot change your own role")

    user.role = new_role
    db.commit()
    db.refresh(user)
    return {"msg": f"User {user.username} promoted to {new_role}"}
