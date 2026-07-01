import redis.asyncio as redis
from sqlalchemy.orm import Session
from decouple import config

from ..schemas import NotificationInput
from ..crud import notifications
from ..database import SessionLocal



""" real_time reading redis stream events """


r = redis.Redis(host=config("HOST"), port=config("PORT"), decode_responses=True)

# User_Service consumer
async def consume_user_events():
    print("Waiting for user_service events...")
    while True:
        events = await r.xreadgroup(
            groupname="notification_group",
            consumername="notification_user_consumer",
            streams={"user_events": ">"},
            block=0
        )

        for stream, messages in events:
            for message_id, data in messages:
                print("consuming")
                event_type = data.get("event")

                db: Session = SessionLocal()
                try:
                    if event_type == "user_created":
                        user_id = int(data["user_id"])
                        nickname = str(data["nickname"])
                        db_notification = NotificationInput(
                            actor_id=user_id,
                            type="user_created",
                            object_type="user",
                            object_id=user_id,
                            expire_days=3,
                            payload={"message": f"{nickname} joined us!"},
                            is_public=True
                        )
                        notifications.create_notification(db, db_notification)
                        print("notification created")

                    elif event_type == "user_deleted":
                        user_id = int(data["user_id"])
                        object_type = "user"
                        notifications.delete_user_notifications(db, user_id)
                        notifications.delete_object_notification(db, object_type, user_id)
                        print("user notifications deleted")

                    elif event_type == "user_updated":
                        user_id = int(data["user_id"])
                        nickname = str(data["nickname"])
                        notifications.update_actor_nickname(db, user_id, nickname)
                        print("actor nickname updated")

                    await r.xack("user_events", "notification_group", message_id)

                except Exception as e:
                    print("Consumer error:", e)
                    db.rollback()

                    await r.xack("user_events", "notification_group", message_id)

                finally:
                    db.close()

# Post_service events
async def consume_post_events():
    print("Waiting for post_service events...")
    while True:
        events = await r.xreadgroup(
            groupname="notification_group",
            consumername="notification_post_consumer",
            streams={"post_events": ">"},
            block=0
        )
        for stream, messages in events:
            for message_id, data in messages:
                print("consuming")
                event_type = data.get("event")

                db: Session = SessionLocal()
                try:
                    if data["event"] == "post_created":
                        post_id = int(data["post_id"])
                        owner_id = int(data["owner_id"])
                        nickname = str(data["nickname"])
                        db_notification = NotificationInput(
                            actor_id=owner_id,
                            type="post_created",
                            object_type="post",
                            object_id=post_id,
                            expire_days=3,
                            payload={"message": f"{nickname} recently posted!"},
                            is_public=True
                        )
                        notifications.create_notification(db, db_notification)
                        print("notification created")

                    elif event_type == "post_deleted":
                        post_id = int(data["post_id"])
                        object_type = "post"
                        notifications.delete_object_notification(db, object_type, post_id)
                        print(f"post notification with {post_id} id deleted")

                    elif event_type == "comment_created":
                        # created reply details
                        comment_id = int(data["comment_id"])
                        actor_id = int(data["actor_id"])
                        nickname = str(data["nickname"])
                        # post that parent comment and reply belongs to it
                        post_id = int(data["post_id"])
                        post_owner = int(data["post_owner"])

                        db_notification = NotificationInput(
                            recipient_id=post_owner,
                            actor_id=actor_id,
                            type="comment_created",
                            object_type="comment",
                            object_id=comment_id,
                            expire_days=1,
                            payload={"message": f"{nickname} replied on your comment!", "post_id": post_id},
                            is_public=False
                        )
                        notifications.create_notification(db, db_notification)
                        print("notification created")

                    await r.xack("post_events", "notification_group", message_id)

                except Exception as e:
                    print("Consumer error:", e)
                    db.rollback()

                    await r.xack("post_events", "notification_group", message_id)

                finally:
                    db.close()

# Comment_Service consumer
async def consume_comment_events():
    print("Waiting for comment_service events...")
    while True:
        events = await r.xreadgroup(
            groupname="notification_group",
            consumername="notification_comment_consumer",
            streams={"comment_events": ">"},
            block=0
        )

        for stream, messages in events:
            for message_id, data in messages:
                print("consuming")
                event_type = data.get("event")

                db: Session = SessionLocal()
                try:
                    if event_type == "reply_created":
                        # parent comment details
                        parent_id = int(data["parent_id"])
                        owner_id = int(data["owner_id"])
                        # created reply details
                        comment_id = int(data["comment_id"])
                        actor_id = int(data["actor_id"])
                        nickname = str(data["nickname"])
                        # post that parent comment and reply belongs to it
                        post_id = int(data["post_id"])

                        db_notification = NotificationInput(
                            recipient_id=owner_id,
                            actor_id=actor_id,
                            type="comment_created",
                            object_type="comment",
                            object_id=comment_id,
                            expire_days=1,
                            payload={"message": f"{nickname} replied on your comment!", "post_id": post_id, "parent_id": parent_id},
                            is_public=False
                        )
                        notifications.create_notification(db, db_notification)
                        print("notification created")

                    elif event_type == "comment_created_meta":
                        # created reply details
                        comment_id = int(data["comment_id"])
                        actor_id = int(data["owner_id"])
                        nickname = str(data["owner_nickname"])
                        post_id = int(data["post_id"])
                        post_owner = int(data["post_owner"])

                        print(comment_id, actor_id, nickname, post_id, post_owner)

                        db_notification = NotificationInput(
                            recipient_id=post_owner,
                            actor_id=actor_id,
                            type="comment_created",
                            object_type="comment",
                            object_id=comment_id,
                            expire_days=1,
                            payload={"message": f"{nickname} leave a comment on your post!", "post_id": post_id},
                            is_public=False
                        )
                        notifications.create_notification(db, db_notification)
                        print("notification created")

                    await r.xack("comment_events", "notification_group", message_id)

                except Exception as e:
                    print("Consumer error:", e)
                    db.rollback()

                    await r.xack("comment_events", "notification_group", message_id)

                finally:
                    db.close()