from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from ..core.security import hash_password, verify_password
from ..models import User


# change password in personal dashboard or forgot password
def change_password(db: Session, user_id: int, current_password: str, new_password: str):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    if not verify_password(current_password, user.hashed_password):
        raise HTTPException(400, "Wrong password")

    user.hashed_password = hash_password(new_password)
    db.commit()
