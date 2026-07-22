from fastapi import Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from typing import Annotated

from .. import models, schemas, database


""" users crud """


# config dependencies
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
db_dependency = Annotated[Session, Depends(database.get_db)]


# get all users data
def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.User).offset(skip).limit(limit).all()

# get user by id
def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

# get user by username
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

# get profile by payload.user_id
def profile(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

# register and create new user
def create_user(db: Session, user: schemas.CreateUserRequest):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="user is already registered!")

    db_user = models.User(
        username = user.username,
        hashed_password = bcrypt_context.hash(user.password),
        nickname=user.nickname,
        email=user.email,
        image_url = "default-avatar.jpg"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

# update some user fields by id
def update_user(db: Session, user_id: int, patch: schemas.UpdateUserRequest):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="user not found!")

    # detect and update every object that writen in body and only them
    for field, value in patch.dict(exclude_unset=True).items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user

# update pending_email field
def change_email(db: Session, user_id: int, pending_email: str):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="user not found!")

    if db_user.email == pending_email:
        raise HTTPException(400, "This is already your current email")

    db_email = (
        db.query(models.User)
        .filter(
            models.User.id != user_id,
            or_(
                models.User.email == pending_email,
                models.User.pending_email == pending_email,
            )
        )
        .first()
    )

    if db_email:
        raise HTTPException(status_code=409, detail="there is already an account with that email!")

    db_user.pending_email = pending_email
    db.commit()

    return db_user

# update verified email field
def verify_email(db: Session, user_id: int, email: str):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="user not found!")

    db_user.email = email
    db_user.is_email_verified = True
    db.commit()

    return {"details": "user verified email changed successfully"}

# delete user by id
def delete_user(db: Session, user_id: int) -> bool:
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True
