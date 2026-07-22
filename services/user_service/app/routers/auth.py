from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Annotated

from .. import database, schemas, dependencies
from ..core import rate_limit
from ..core.security import authenticate_user, create_access_token, refresh_user_access_token


""" auth routers """


# routers prefix configuration
router = APIRouter(prefix="/auth", tags=["auth"])

# config dependencies
db_dependency = Annotated[Session, Depends(database.get_db)]


# login API for authentication users and return token if it was valid
@router.post(
    "/token",
    dependencies=[rate_limit.rate_limit(limit=20, window=300)],
    response_model=schemas.Token
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency
):
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    access_token = create_access_token(
        data={
            "sub": user.username,
            "id": user.id,
            "nickname": user.nickname,
            "role": user.role,
            "is_verified": user.is_email_verified,
        },
        expire_delta=timedelta(minutes=60)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# refresh and recreate jwt token for user
@router.post(
    "/refresh-user-token/",
    dependencies=[Depends(dependencies.internal_service_required),rate_limit.rate_limit(limit=20, window=300)]
)
def refresh_user_token(
    db: Session = Depends(database.get_db),
    current_user = Depends(dependencies.get_current_user)
):
    user_id = current_user["user_id"]

    access_token = refresh_user_access_token(
        db=db,
        user_id=user_id
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
