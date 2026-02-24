from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from decouple import config
from redis.exceptions import ResponseError
import redis.asyncio as redis
import asyncio

from .events.consumer import consume_user_events, consume_post_deleted
from . import models, database
from .routers import avatar, media


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

models.Base.metadata.create_all(bind=database.engine)

# FastAPI app config
app = FastAPI(title="Media Service")

app.mount("/media", StaticFiles(directory="media"), name="media")

# include routers
app.include_router(avatar.router)
app.include_router(media.router)


r = redis.Redis(host=config("HOST"), port=config("PORT"), decode_responses=True)

# Ensure the Redis Stream consumer group exists before starting the consumer
async def ensure_groups():
    streams = ["user_events", "post_events"]

    for stream in streams:
        try:
            await r.xgroup_create(
                name=stream,
                groupname="media_group",
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
    asyncio.create_task(consume_post_deleted())