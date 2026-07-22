from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import timedelta, datetime
from passlib.context import CryptContext
from decouple import config
from jose import jwt

from .. import models


""" authentication and authorization definitions"""


# secret key and algorithm configuration for preventing information hijack
SECRET_KEY = config("SECRET_KEY")
ALGORITHM = config("ALGORITHM")

# encrypt passwords to hashed passwords
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# check user username and password for login
def authenticate_user(username: str, password: str, db):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return None
    # check the hashed received password with database hashed password
    if not bcrypt_context.verify(password, user.hashed_password):
        return None
    return user

# create and return access token for login authorization
def create_access_token(data: dict, expire_delta: timedelta):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + expire_delta

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# recreate and return new access token
def refresh_user_access_token(db: Session, user_id: int):

    user = (
        db.query(models.User)
        .filter(models.User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    token_data = {
        "id": user.id,
        "sub": user.username,
        "nickname": user.nickname,
        "role": user.role,
        "is_verified": user.is_email_verified,
    }

    return create_access_token(
        data=token_data,
        expire_delta=timedelta(minutes=60)
    )

# encrypting normal password into hashed password
def hash_password(password: str):
    return bcrypt_context.hash(password)

# decrypting hashed password into normal password
def verify_password(plain: str, hashed: str):
    return bcrypt_context.verify(plain, hashed)
