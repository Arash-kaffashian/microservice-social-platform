from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from email.message import EmailMessage
from decouple import config
import smtplib
import uuid

from ..models import User


""" email definitions """


# source email configuration
EMAIL = config("EMAIL")
APP_PASSWORD = config("APP_PASSWORD")

# verification link from email sending expire time
EMAIL_TOKEN_EXPIRE_MINUTES = 10


# request email change in personal dashboard
def request_email_change(db: Session, user_id: int, new_email: str):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    token = str(uuid.uuid4())

    user.pending_email = new_email
    user.email_verify_token = token
    user.email_verify_expire = datetime.utcnow() + timedelta(minutes=EMAIL_TOKEN_EXPIRE_MINUTES)
    user.is_email_verified = False

    db.commit()

    send_verification_email(new_email, token)

# verification answered verify link
def verify_email(db: Session, token: str):
    user = db.query(User).filter(User.email_verify_token == token).first()
    if not user:
        raise HTTPException(400, "Invalid token")

    if user.email_verify_expire < datetime.utcnow():
        raise HTTPException(400, "Token expired")

    user.email = user.pending_email or user.email
    user.pending_email = None
    user.email_verify_token = None
    user.email_verify_expire = None
    user.is_email_verified = True

    db.commit()

# sending verification email to targeted email from our source email
def send_verification_email(to_email: str, token: str):
    verify_link = f"http://localhost:8000/api/settings/verify/{token}"
    # email configuration
    msg = EmailMessage()
    msg["Subject"] = "Verify your email"
    msg["From"] = EMAIL
    msg["To"] = to_email
    msg.set_content(f"Click to verify: {verify_link}")

    # smtplib configuration
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL, APP_PASSWORD)
        smtp.send_message(msg)
