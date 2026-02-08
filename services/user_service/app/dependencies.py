from fastapi import Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from decouple import config

from .database import get_db
from .models import User


""" basic dependencies like access permission rules """


# config secret key and algorithm based on .env file to prevent information hijack
SECRET_KEY = config("SECRET_KEY")
ALGORITHM = config("ALGORITHM")

# config oauth2 token url path
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")

# config internal token for internal api calls
INTERNAL_TOKEN = config("INTERNAL_SERVICE_TOKEN")


# login access permission check
async def get_current_user(token: str = Depends(oauth2_bearer),db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int | None = payload.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

# internal access permission check
def internal_service_required(x_internal_token: str = Header(...)):
    if x_internal_token != INTERNAL_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Internal service access only"
        )

# verified access permission check
def verified_user_required(user: User = Depends(get_current_user)):
    if not user.is_email_verified:
        raise HTTPException(
            status_code=403,
            detail="Email not verified"
        )
    return user

# admin access permission check
def admin_required(user=Depends(get_current_user)):
    if user.role not in ("admin", "superadmin"):
        raise HTTPException(403, "Admin access required")
    return user

# superadmin access permission check
def superadmin_required(user=Depends(get_current_user)):
    if user.role != "superadmin":
        raise HTTPException(403, "SuperAdmin only")
    return user
