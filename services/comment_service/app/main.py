from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from redis.exceptions import ResponseError
from decouple import config
from fastapi_swagger import patch_fastapi
import redis.asyncio as redis
import asyncio

from .events.consumer import consume_user_events, consume_post_events
from . import models, database
from .routers import comments, replies


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

models.Base.metadata.create_all(bind=database.engine)

# FastAPI app config
app = FastAPI(title="Comment Service",docs_url=None,swagger_ui_oauth2_redirect_url=None)
patch_fastapi(app)

# include routers
app.include_router(comments.router)
app.include_router(replies.router)


r = redis.Redis(host=config("HOST"), port=config("PORT"), decode_responses=True)

# Ensure the Redis Stream consumer group exists before starting the consumer
async def ensure_groups():
    streams = ["user_events", "comment_events", "post_events", "notification_events"]

    for stream in streams:
        try:
            await r.xgroup_create(
                name=stream,
                groupname="comment_group",
                id="0",
                mkstream=True
            )
            print(f"Consumer group created for {stream}")
        except ResponseError as e:
            if "BUSYGROUP" in str(e):
                print(f"Consumer group already exists for {stream}")
            else:
                raise



@app.on_event("startup")
async def startup_event():
    # create Redis stream and consumer group
    await ensure_groups()

    # start consumer in background
    asyncio.create_task(consume_user_events())
    asyncio.create_task(consume_post_events())