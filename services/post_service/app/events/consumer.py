import redis.asyncio as redis
from sqlalchemy.orm import Session
from decouple import config

from ..database import SessionLocal
from ..crud import delete_user_posts
from ..events.publisher import publish_post_deleted


""" real_time reading redis stream events """


r = redis.Redis(host=config("HOST"), port=config("PORT"), decode_responses=True)

# this definition wait for redis stream user_deleted event to delete its posts too
async def consume_user_deleted():

    while True:
        events = await r.xreadgroup(
            groupname="post_group",
            consumername="post_consumer",
            streams={"user_events": ">"},
            block=0
        )

        for stream, messages in events:
            for message_id, data in messages:

                if data["event"] == "user_deleted":
                    user_id = int(data["user_id"])

                    db: Session = SessionLocal()
                    try:
                        posts = delete_user_posts(db, user_id)
                    finally:
                        db.close()

                    # sending event for each deleted post
                    for post in posts:
                        await publish_post_deleted(post.id)

                    # delete user_deleted event from redis steam pending list
                    await r.xack("user_events", "post_group", message_id)
