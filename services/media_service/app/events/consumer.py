import redis.asyncio as redis
from sqlalchemy.orm import Session
from decouple import config

from ..database import SessionLocal
from ..crud import avatar_crud, media_crud


""" real_time reading redis stream events """


r = redis.Redis(host=config("HOST"), port=config("PORT"), decode_responses=True)

# this definition wait for redis stream user_created event to create_avatar_record for it
async def consume_user_events():
    print("Waiting for user_created events...")
    while True:
        events = await r.xreadgroup(
            groupname="media_group",
            consumername="media_user_consumer",
            streams={"user_events": ">"},
            block=5000
        )

        for stream, messages in events:
            for message_id, data in messages:
                print("consuming")
                event_type = data.get("event")

                db: Session = SessionLocal()
                try:
                    if event_type == "user_created":
                        user_id = int(data["user_id"])
                        avatar_crud.create_avatar_record(db, owner_id=user_id)
                        print("created done")

                    elif event_type == "user_deleted":
                        user_id = int(data["user_id"])
                        avatar_crud.delete_avatar(db, user_id)
                        print("deleted done")

                    await r.xack("user_events", "media_group", message_id)

                except Exception as e:
                    print("Consumer error:", e)
                    db.rollback()

                    await r.xack("user_events", "media_group", message_id)

                finally:
                    db.close()

# this definition wait for redis stream post_deleted event to delete its medias
async def consume_post_deleted():
    print("Waiting for post_deleted events...")
    while True:
        events = await r.xreadgroup(
            groupname="media_group",
            consumername="media_post_consumer",
            streams={"post_events": ">"},
            block=0
        )
        for stream, messages in events:
            for message_id, data in messages:

                if data["event"] == "post_deleted":
                    post_id = int(data["post_id"])
                    db: Session = SessionLocal()
                    try:
                        media_crud.delete_post_medias(db, post_id)
                    finally:
                        db.close()

                    # delete post_deleted event from redis steam pending list
                    await r.xack("post_events", "media_group", message_id)