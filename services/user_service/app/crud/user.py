from fastapi import Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from typing import Annotated

from .. import models, schemas, database
from ..core.email import request_email_change


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

    # send email verification to user email
    try:
        request_email_change(
            db=db,
            user_id=db_user.id,
            new_email=db_user.email
        )
    except Exception as e:
        print("Email sending failed:", e)

    return db_user

# update some user fields by id
def update_user(db: Session, user_id: int, patch: schemas.UpdateUserRequest):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None

    # detect and update every object that writen in body and only them
    for field, value in patch.dict(exclude_unset=True).items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user

# delete user by id
def delete_user(db: Session, user_id: int) -> bool:
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True
