from sqlalchemy.orm import Session
import redis.asyncio as redis
from decouple import config

from ..database import SessionLocal
from ..crud import comments


""" real_time reading redis stream events """


r = redis.Redis(host=config("HOST"), port=config("PORT"), decode_responses=True)

# this definition wait for redis stream post_service events
async def consume_post_events():

    while True:
        events = await r.xreadgroup(
            groupname="comment_group",
            consumername="comment_consumer",
            streams={"post_events": ">"},
            block=0
        )

        for stream, messages in events:
            for message_id, data in messages:

                if data["event"] == "post_deleted":
                    post_id = int(data["post_id"])

                    db: Session = SessionLocal()
                    try:
                        comments.delete_post_comments(db, post_id)
                    finally:
                        db.close()

                    # delete post_deleted event from redis steam pending list
                    await r.xack("post_events", "comment_group", message_id)


# this definition wait for redis stream user_service events
async def consume_user_events():

    while True:
        events = await r.xreadgroup(
            groupname="comment_group",
            consumername="comment_consumer",
            streams={"user_events": ">"},
            block=0
        )

        for stream, messages in events:
            for message_id, data in messages:

                if data["event"] == "user_updated":
                    user_id = int(data["user_id"])
                    new_nickname = str(data["nickname"])

                    db: Session = SessionLocal()
                    try:
                        comments.update_comments_nickname(db, user_id, new_nickname)
                    finally:
                        db.close()

                    # delete user_event from redis_steam pending list
                    await r.xack("user_events", "comment_group", message_id)
