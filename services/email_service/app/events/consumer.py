from sqlalchemy.orm import Session
import redis.asyncio as redis
from decouple import config

from ..database import SessionLocal
from ..crud import verification
from ..tasks import system_email


""" real_time reading redis stream events """


r = redis.Redis(host=config("HOST"), port=config("PORT"), decode_responses=True)

# this definition wait for redis stream user_service events
async def consume_user_events():

    while True:
        events = await r.xreadgroup(
            groupname="email_group",
            consumername="email_consumer",
            streams={"user_events": ">"},
            block=0
        )

        for stream, messages in events:
            for message_id, data in messages:

                # user_created consumer
                if data["event"] == "user_created":
                    user_id = int(data["user_id"])
                    email = str(data["email"])

                    db: Session = SessionLocal()
                    try:
                        # create database record for new users and send them verification email
                        db_email = verification.create_record(db, user_id, email)
                        system_email.send_verification_email.delay(db_email.email, db_email.token)
                    finally:
                        db.close()

                    await r.xack("user_events", "email_group", message_id)

                # change_email_request consumer
                if data["event"] == "change_email_request":
                    user_id = int(data["user_id"])
                    new_email = str(data["pending_email"])

                    db: Session = SessionLocal()
                    try:
                        # change database record and send new verification link to new email
                        db_email = verification.change_email(db, user_id, new_email)
                        system_email.send_verification_email.delay(db_email["email"], db_email["token"])
                    finally:
                        db.close()

                    await r.xack("user_events", "email_group", message_id)
