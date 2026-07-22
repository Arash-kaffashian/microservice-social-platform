from fastapi import HTTPException

from ..schemas import CreateUserRequest, UpdateUserRequest
from ..crud import user
from ..events import publisher


""" router and crud bridge """


# bridge between router and crud to publish user_deleted for other services
async def delete_user(db, user_id: int):
    db_user = user.delete_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    await publisher.publish_user_deleted(user_id)
    return {"detail": "User deleted successfully"}

# bridge between router and crud to publish user_created for other services
async def create_user(db, user_data: CreateUserRequest):
    db_user = user.create_user(db, user_data)
    if not db_user:
        raise HTTPException(status_code=400, detail="bad request")

    await publisher.publish_user_created(db_user.id, db_user.nickname, db_user.email)
    return db_user

# bridge between router and crud to publish user_updated for other services
async def update_user(db, user_id: int, user_data: UpdateUserRequest):
    db_user = user.update_user(db, user_id, user_data)
    if not db_user:
        raise HTTPException(status_code=400, detail="bad request")

    await publisher.publish_user_updated(db_user.id, db_user.nickname)
    return db_user

# bridge between router and crud to publish change_email_request for other services
async def change_email(db, user_id: int, new_email: str):
    db_user = user.change_email(db, user_id, new_email)
    if not db_user:
        raise HTTPException(status_code=400, detail="bad request")

    await publisher.publish_change_email_request(db_user.id, db_user.pending_email)
    return {"message": "Verification email sent"}
