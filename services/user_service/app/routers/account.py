from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from .. import database, schemas, models, dependencies
from ..core import rate_limit
from ..core.email import request_email_change, verify_email, send_verification_email


# routers prefix configuration
router = APIRouter(prefix="/settings", tags=["settings"])

# change email API for changing email and resend verify link
@router.post("/change-email", dependencies=[rate_limit.rate_limit(limit=1, window=259200),])
def change_email(
    data: schemas.ChangeEmailRequest,
    db: Session = Depends(database.get_db),
    current_user=Depends(dependencies.get_current_user)
):
    request_email_change(db, current_user.id, data.new_email)
    return {"message": "Verification email sent"}

# resend verify link to user email if its not verified
@router.post("/resend-verify", dependencies=[rate_limit.rate_limit(limit=5, window=3600)])
def resend_verify_email(
    db: Session = Depends(database.get_db),
    current_user=Depends(dependencies.get_current_user)
):
    user: models.User = db.get(models.User, current_user.id)

    if user.is_email_verified:
        raise HTTPException(400, "Email already verified")

    if not user.email_verify_token or user.email_verify_expire < datetime.utcnow():
        user.email_verify_token = str(uuid.uuid4())
        user.email_verify_expire = datetime.utcnow() + timedelta(hours=24)

    db.commit()
    send_verification_email(user.email, user.email_verify_token)

    return {"message": "Verification email resent"}

# submitting email verify links
@router.get("/verify", dependencies=[rate_limit.rate_limit(limit=5, window=3600)])
def verify_user_email(
    token: str,
    db: Session = Depends(database.get_db)
):
    verify_email(db, token)
    return {"message": "Email verified successfully"}
