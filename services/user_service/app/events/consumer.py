import redis.asyncio as redis
from sqlalchemy.orm import Session
from decouple import config


from ..schemas import UpdateUserRequest
from ..database import SessionLocal
from ..crud import user


""" real_time reading redis stream events """


r = redis.Redis(host=config("HOST"), port=config("PORT"), decode_responses=True)

# consume avatar_events from redis stream
async def consume_avatar_events():

    while True:
        events = await r.xreadgroup(
            groupname="user_group",
            consumername="user_consumer",
            streams={"media_events": ">"},
            block=0
        )

        for stream, messages in events:
            for message_id, data in messages:

                if data["event"] == "avatar_updated":
                    user_id = int(data["user_id"])
                    url = data["url"]

                    db: Session = SessionLocal()
                    try:
                        patch = UpdateUserRequest(image_url=url)
                        user.update_user(db, user_id, patch)
                    except Exception as e:
                        print("ERROR:", e)
                        db.rollback()
                    finally:
                        db.close()

                    # delete avatar_updated event from redis steam pending list
                    await r.xack("media_events", "user_group", message_id)


# consume email_events from redis stream
async def consume_email_events():

    while True:
        events = await r.xreadgroup(
            groupname="user_group",
            consumername="user_consumer",
            streams={"email_events": ">"},
            block=0
        )

        for stream, messages in events:
            for message_id, data in messages:

                # email_verified consumer
                if data["event"] == "email_verified":
                    user_id = int(data["user_id"])
                    email = str(data["email"])

                    db: Session = SessionLocal()
                    try:
                        # update user email field with verified email
                        user.verify_email(db, user_id, email)
                    except Exception as e:
                        print("ERROR:", e)
                        db.rollback()
                    finally:
                        db.close()

                    # delete email_verified event from redis steam pending list
                    await r.xack("email_events", "user_group", message_id)
