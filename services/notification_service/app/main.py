from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from decouple import config
from redis.exceptions import ResponseError
from fastapi_swagger import patch_fastapi
import redis.asyncio as redis
import asyncio

from .events.consumer import consume_user_events, consume_post_events, consume_comment_events
from . import models, database
from .routers import notifications


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

models.Base.metadata.create_all(bind=database.engine)

# FastAPI app config
app = FastAPI(title="Notification Service",docs_url=None,swagger_ui_oauth2_redirect_url=None)
patch_fastapi(app)

# include routers
app.include_router(notifications.router)


r = redis.Redis(host=config("HOST"), port=config("PORT"), decode_responses=True)

# Ensure the Redis Stream consumer group exists before starting the consumer
async def ensure_groups():
    streams = ["user_events", "media_events", "post_events", "comment_events"]

    for stream in streams:
        try:
            await r.xgroup_create(
                name=stream,
                groupname="notification_group",
                id="0",
                mkstream=True
            )
            print(f"Consumer group created for {stream}")
        except ResponseError as e:
            if "BUSYGROUP" in str(e):
                print(f"Consumer group already exists for {stream}")
            else:
                raise


# application startup for ensure and consumes start
@app.on_event("startup")
async def startup_event():
    await ensure_groups()
    asyncio.create_task(consume_user_events())
    asyncio.create_task(consume_post_events())
    asyncio.create_task(consume_comment_events())