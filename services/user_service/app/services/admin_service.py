from ..crud import admin
from ..events.publisher import publish_user_created


""" router and crud bridge """


# bridge between router and crud to publish user_created for other services
async def create_superadmin(db):
    db_user = admin.create_superadmin(db)

    await publish_user_created(db_user.id)
    return db_user
