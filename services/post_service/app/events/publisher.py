import redis.asyncio as redis
from decouple import config


""" pushing redis stream events """


r = redis.Redis(host=config("HOST"), port=config("PORT"), decode_responses=True)

# publish redis stream post_created events
async def publish_post_created(post_id: int, owner_id:int, title:str, nickname:str):
    await r.xadd(
        "post_events",
        {
            "event": "post_created",
            "post_id": int(post_id),
            "owner_id": int(owner_id),
            "nickname": str(nickname),
            "title": str(title),
        }
    )

# publish redis stream post_deleted events
async def publish_post_deleted(post_id: int):
    await r.xadd(
        "post_events",
        {
            "event": "post_deleted",
            "post_id": int(post_id),
        }
    )

# publish redis stream comment_created events
async def publish_comment_created(post_id: int, post_owner:int, owner_id:int, owner_nickname:str, comment_id:int):
    await r.xadd(
        "comment_events",
        {
            "event": "comment_created_meta",
            "post_id": int(post_id),
            "post_owner": int(post_owner),
            "owner_id": int(owner_id),
            "owner_nickname": str(owner_nickname),
            "comment_id": int(comment_id),
        }
    )