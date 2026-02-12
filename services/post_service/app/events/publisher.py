import redis.asyncio as redis
from decouple import config


""" pushing redis stream events """


r = redis.Redis(host=config("HOST"), port=config("PORT"), decode_responses=True)

# publish redis stream post_deleted events
async def publish_post_deleted(post_id: int):
    await r.xadd(
        "post_events",
        {
            "event": "post_deleted",
            "post_id": str(post_id),
        }
    )
