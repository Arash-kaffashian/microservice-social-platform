from sqlalchemy.orm import Session
import redis.asyncio as redis
from decouple import config

from ..database import SessionLocal
from ..crud.comments import delete_post_comments


""" real_time reading redis stream events """


r = redis.Redis(host=config("HOST"), port=config("PORT"), decode_responses=True)

# this definition wait for redis stream post_deleted event to delete its comments/replies too
async def consume_post_deleted():

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
                        delete_post_comments(db, post_id)
                    finally:
                        db.close()

                    # delete post_deleted event from redis steam pending list
                    await r.xack("post_events", "comment_group", message_id)
