import redis.asyncio as redis
from decouple import config


""" pushing redis stream events """


r = redis.Redis(host=config("HOST"), port=config("PORT"), decode_responses=True)

# publish redis stream comment_created event
async def publish_comment_created(comment_id: int, owner_id:int, nickname:str, post_id:int):
    await r.xadd(
        "comment_events",
        {
            "event": "comment_created",
            "comment_id": int(comment_id),
            "owner_id": int(owner_id),
            "nickname": str(nickname),
            "post_id": int(post_id),
        }
    )

# publish redis stream reply_created event
async def publish_reply_created(comment_id: int, actor_id:int, nickname:str, parent_id:int, owner_id:int, post_id:int):
    await r.xadd(
        "comment_events",
        {
            "event": "reply_created",
            "comment_id": int(comment_id),
            "actor_id": int(actor_id),
            "nickname": str(nickname),
            "post_id": int(post_id),
            "parent_id":int(parent_id),
            "owner_id":int(owner_id)
        }
    )

# publish redis stream comment_deleted event
async def publish_comment_deleted(comment_id: int):
    await r.xadd(
        "comment_events",
        {
            "event": "comment_deleted",
            "comment_id": int(comment_id),
        }
    )
