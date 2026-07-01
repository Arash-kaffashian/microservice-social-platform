import redis.asyncio as redis
from sqlalchemy.orm import Session
from decouple import config

from ..database import SessionLocal
from ..crud import delete_user_posts, update_posts_nickname, get_post
from ..schemas import NotificationInput
from ..events.publisher import publish_post_deleted, publish_comment_created


""" real_time reading redis stream events """


r = redis.Redis(host=config("HOST"), port=config("PORT"), decode_responses=True)

# this definition wait for redis stream user_events
async def consume_user_events():

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

                if data["event"] == "user_updated":
                    user_id = int(data["user_id"])
                    nickname = str(data["nickname"])

                    db: Session = SessionLocal()
                    try:
                        update_posts_nickname(db, user_id, nickname)
                    finally:
                        db.close()

                    # delete user_updated event from redis steam pending list
                    await r.xack("user_events", "post_group", message_id)

# this definition wait for redis stream comment_events
async def consume_comment_events():

    while True:
        events = await r.xreadgroup(
            groupname="post_group",
            consumername="post_consumer",
            streams={"comment_events": ">"},
            block=0
        )

        for stream, messages in events:
            for message_id, data in messages:
                print("consuming")
                event_type = data.get("event")

                db: Session = SessionLocal()
                try:
                    if event_type == "comment_created":
                        comment_id = int(data["comment_id"])
                        actor_id = int(data["owner_id"])
                        nickname = str(data["nickname"])
                        post_id = int(data["post_id"])

                        db_post = get_post(db, post_id)

                        db_notification = NotificationInput(
                        post_id = post_id,
                        post_owner = db_post.owner_id,
                        owner_id = actor_id,
                        owner_nickname = nickname,
                        comment_id = comment_id
                        )

                        print(comment_id, actor_id, nickname, post_id, db_notification.post_owner)
                        await publish_comment_created(
                            db_notification.post_id,
                            db_notification.post_owner,
                            db_notification.owner_id,
                            db_notification.owner_nickname,
                            db_notification.comment_id,
                        )

                    await r.xack("comment_events", "notification_group", message_id)

                except Exception as e:
                    print("Consumer error:", e)
                    db.rollback()

                    await r.xack("comment_events", "notification_group", message_id)


                # delete event from redis steam pending list
                await r.xack("user_events", "post_group", message_id)