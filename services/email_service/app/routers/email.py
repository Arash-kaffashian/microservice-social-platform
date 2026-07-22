from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import database
from ..core import rate_limit
from ..services import email_service
from ..dependencies import internal_service_required, get_current_user
from ..crud import verification
from ..tasks import system_email


""" Email routers """


# routers setup
router = APIRouter()

# verify email with verification link + token
@router.get("/emails/verify", dependencies=[rate_limit.rate_limit(limit=20, window=300)])
async def verify_email(token: str, db: Session = Depends(database.get_db)):
    return await email_service.verify_email(db, token)

# resend verify link to user email
@router.post("/emails/resend-verify/", dependencies=[Depends(internal_service_required), rate_limit.rate_limit(limit=10, window=300)])
def resend_verify_email(
    db: Session = Depends(database.get_db),
    user=Depends(get_current_user)
):
    user_id = user["user_id"]
    user_db = verification.recreate_token(db, user_id)

    # send verification token to user email
    system_email.send_verification_email(user_db["email"], user_db["token"])

    return {"message": "Verification email resent"}
