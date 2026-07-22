from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from ..models import EmailVerification


""" Email crud """


# verification link expire time
EMAIL_TOKEN_EXPIRE_MINUTES = 10

# recreate verification token
def recreate_token(db: Session, user_id: int):
    email_db = db.query(EmailVerification).filter(EmailVerification.user_id == user_id).first()
    if not email_db:
        raise HTTPException(status_code=404, detail="user not found!")

    if email_db.is_verified:
        raise HTTPException(status_code=405, detail="email already verified!")

    # create new token
    token = str(uuid.uuid4())

    email_db.token = token
    email_db.expire_at = datetime.utcnow() + timedelta(minutes=EMAIL_TOKEN_EXPIRE_MINUTES)

    db.commit()

    return {"email": email_db.email, "token": email_db.token}

# create database record for new users
def create_record(db: Session, user_id: int, email: str):
    email_db = db.query(EmailVerification).filter(EmailVerification.user_id == user_id).first()
    if email_db:
        raise HTTPException(status_code=404, detail="verification record already exist!")

    # create a token for verification link
    token = str(uuid.uuid4())

    email_db = EmailVerification(
        user_id=user_id,
        email=email,
        token=token,
        expire_at=datetime.utcnow() + timedelta(minutes=EMAIL_TOKEN_EXPIRE_MINUTES),
        is_verified=False,
    )

    db.add(email_db)
    db.commit()
    db.refresh(email_db)

    return email_db

# verify token link
def verify(db: Session, token: str):
    email_db = db.query(EmailVerification).filter(EmailVerification.token == token).first()
    if not email_db:
        raise HTTPException(status_code=404, detail="Invalid Token!")

    if email_db.expire_at < datetime.utcnow():
        raise HTTPException(status_code=405, detail="Token expired!")

    # change database record (verified)
    email_db.token = None
    email_db.expire_at = None
    email_db.is_verified = True

    db.commit()

    return {"user_id": email_db.user_id, "email": email_db.email}

# change Verification email record and token field
def change_email(db: Session, user_id: int, new_email: str):
    email_db = db.query(EmailVerification).filter(EmailVerification.user_id == user_id).first()
    if not email_db:
        raise HTTPException(404, "User not found!")

    # create new token
    token = str(uuid.uuid4())

    # change database record
    email_db.email = new_email
    email_db.token = token
    email_db.expire_at = datetime.utcnow() + timedelta(minutes=EMAIL_TOKEN_EXPIRE_MINUTES)
    email_db.is_verified = False

    db.commit()

    return {"email": email_db.email, "token": email_db.token}