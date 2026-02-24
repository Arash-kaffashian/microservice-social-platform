from fastapi import UploadFile

from ..crud import avatar_crud
from ..events.publisher import publish_avatar_updated


""" router and crud bridge """


# bridge between router and crud to publish avatar_updated for other services
async def avatar_updated(db, owner_id: int, file: UploadFile):
    db_user = await avatar_crud.update_avatar(db, owner_id, file)

    await publish_avatar_updated(user_id=owner_id,url=db_user.url)
    return db_user

# bridge between router and crud to publish avatar_updated for other services
async def set_default(db, owner_id: int):
    db_user = await avatar_crud.set_default(db, owner_id)

    await publish_avatar_updated(user_id=owner_id,url=db_user.url)
    return db_user
