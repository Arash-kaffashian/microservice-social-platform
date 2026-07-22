import redis.asyncio as redis
from decouple import config


""" pushing redis stream events """


r = redis.Redis(host=config("HOST"), port=config("PORT"), decode_responses=True)

# publish redis stream email_verified event
async def publish_email_verified(user_id: int, email:str):
    await r.xadd(
        "email_events",
        {
            "event": "email_verified",
            "user_id": int(user_id),
            "email": str(email),
        }
    )
