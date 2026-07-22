from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from .. import database, schemas, dependencies
from ..core import rate_limit
from ..services.user_service import change_email


""" account setting routers """


# routers prefix configuration
router = APIRouter(prefix="/settings", tags=["settings"])

# request for changing email and send verify link
@router.post("/change-email", dependencies=[rate_limit.rate_limit(limit=6, window=259200)])
async def change_email_request(
    data: schemas.ChangeEmailRequest,
    db: Session = Depends(database.get_db),
    current_user = Depends(dependencies.get_current_user)
):
    user_id = current_user["user_id"]
    return await change_email(db, user_id, data.new_email)
