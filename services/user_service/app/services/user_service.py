from fastapi import HTTPException

from ..crud import user
from ..events.publisher import publish_user_deleted


""" router and crud bridge """


# bridge between router and crud to publish user_deleted for other services
async def delete_user(db, user_id: int):
    db_user = user.delete_user(db, user_id)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    await publish_user_deleted(user_id)

    return {"detail": "User deleted successfully"}
