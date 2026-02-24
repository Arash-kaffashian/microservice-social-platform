import redis.asyncio as redis
from decouple import config


""" pushing redis stream events """


r = redis.Redis(host=config("HOST"), port=config("PORT"), decode_responses=True)

# publish redis stream avatar_updated events
async def publish_avatar_updated(user_id: int, url: str):
    await r.xadd(
        "media_events",
        {
            "event": "avatar_updated",
            "user_id": str(user_id),
            "url": str(url),
        }
    )