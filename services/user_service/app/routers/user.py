from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import database, schemas
from ..dependencies import admin_required, internal_service_required, get_current_user
from ..core import rate_limit
from ..crud import user as user_crud


""" user routers """


# routers prefix configuration
router = APIRouter(prefix="/users", tags=["users"])


# get all users data
@router.get("/", dependencies=[Depends(internal_service_required)], response_model=List[schemas.PublicUserResponse])
def get_users(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    return user_crud.get_users(db, skip, limit)

# get user by username
@router.get("/username={username}", dependencies=[Depends(internal_service_required)], response_model=schemas.PublicUserResponse)
def get_user_by_username(username: str, db: Session = Depends(database.get_db)):
    db_user = user_crud.get_user_by_username(db, username)
    if not db_user:
        raise HTTPException(status_code=404, detail="username not found")
    return db_user

# get user by id
@router.get("/id={user_id}", dependencies=[Depends(internal_service_required)], response_model=schemas.PublicUserResponse)
def get_user_by_id(user_id: int, db: Session = Depends(database.get_db)):
    db_user = user_crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="user_id not found")
    return db_user

@router.get("/profile", dependencies=[rate_limit.rate_limit(limit=60, window=60)], response_model=schemas.ProfileUserResponse)
def get_profile(db: Session = Depends(database.get_db), current_user: schemas.ProfileUserResponse = Depends(get_current_user)):
    return user_crud.get_user_by_id(db, current_user.id)

# create user
@router.post("/", dependencies=[rate_limit.rate_limit(limit=3, window=3600)], status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
async def create_user(user: schemas.CreateUserRequest,db: Session = Depends(database.get_db)):
    db_user = user_crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="this user is already exist")
    return user_crud.create_user(db, user)

# delete user by id
@router.delete("/admin/users/{user_id}", dependencies=[rate_limit.rate_limit(limit=20, window=60)], status_code=status.HTTP_200_OK)
def admin_delete_user(
    user_id: int,
    db: Session = Depends(database.get_db),
    admin: schemas.UserResponse = Depends(admin_required)
):
    db_user = user_crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(404, "User not found")

    if db_user.role in ("admin", "superadmin"):
        raise HTTPException(403, "Cannot delete admin or superadmin")

    if user_crud.delete_user(db, user_id):
        return {"detail": "user has been deleted"}

# Update user (Admin)
@router.patch("/admin/users/{user_id}", dependencies=[rate_limit.rate_limit(limit=20, window=60)], response_model=schemas.UserResponse)
def admin_update_user(
    patch: schemas.UpdateUserRequest,
    user_id: int,
    db: Session = Depends(database.get_db),
    admin: schemas.UserResponse = Depends(admin_required)
):
    db_user = user_crud.update_user(db, user_id, patch)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Delete own account
@router.delete("/me", status_code=status.HTTP_200_OK)
def delete_self(
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    user = user_crud.delete_user(db, current_user.id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return {"detail": "Your account has been deleted"}

# Update own account
@router.patch("/me", dependencies=[rate_limit.rate_limit(limit=20, window=60)], response_model=schemas.ProfileUserResponse)
def update_self(
    patch: schemas.UpdateUserRequest,
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    db_user = user_crud.update_user(db, current_user.id, patch)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
