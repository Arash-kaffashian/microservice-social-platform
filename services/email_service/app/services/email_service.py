from fastapi import HTTPException

from ..crud import verification as crud
from ..events.publisher import publish_email_verified


""" router and crud bridge """


# bridge between router and crud to publish_email_verified for other services
async def verify_email(db, token: str):
    db_user = crud.verify(db, token)
    if not db_user:
        raise HTTPException(status_code=400, detail="something went wrong!")

    # publish user email verified for user_service
    await publish_email_verified(db_user["user_id"], db_user["email"])
    return {"detail": "email verified successfully!"}

