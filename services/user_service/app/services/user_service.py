from fastapi import HTTPException

from ..schemas import CreateUserRequest, UpdateUserRequest
from ..crud import user
from ..events.publisher import publish_user_deleted, publish_user_created, publish_user_updated


""" router and crud bridge """


# bridge between router and crud to publish user_deleted for other services
async def delete_user(db, user_id: int):
    db_user = user.delete_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    await publish_user_deleted(user_id)
    return {"detail": "User deleted successfully"}

# bridge between router and crud to publish user_created for other services
async def create_user(db, user_data: CreateUserRequest):
    db_user = user.create_user(db, user_data)
    if not db_user:
        raise HTTPException(status_code=400, detail="bad request")

    await publish_user_created(db_user.id, db_user.nickname)
    return db_user

# bridge between router and crud to publish user_updated for other services
async def update_user(db, user_id: int, user_data: UpdateUserRequest):
    db_user = user.update_user(db, user_id, user_data)
    if not db_user:
        raise HTTPException(status_code=400, detail="bad request")

    await publish_user_updated(db_user.id, db_user.nickname)
    return db_user
