import redis.asyncio as redis
from decouple import config


""" pushing redis stream events """


r = redis.Redis(host=config("HOST"), port=config("PORT"), decode_responses=True)

# publish redis stream user_deleted events
async def publish_user_deleted(user_id: int):
    await r.xadd(
        "user_events",
        {
            "event": "user_deleted",
            "user_id": str(user_id),
        }
    )

# publish redis stream user_created events
async def publish_user_created(user_id: int):
    await r.xadd(
        "user_events",
        {
            "event": "user_created",
            "user_id": str(user_id),
        }
    )