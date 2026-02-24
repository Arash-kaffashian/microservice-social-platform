from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from redis.exceptions import ResponseError
from decouple import config
import redis.asyncio as redis
import asyncio

from .events.consumer import consume_post_deleted
from . import models, database
from .routers import comments, replies


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

models.Base.metadata.create_all(bind=database.engine)

# FastAPI app config
app = FastAPI(title="Comment Service")

# include routers
app.include_router(comments.router)
app.include_router(replies.router)


r = redis.Redis(host=config("HOST"), port=config("PORT"), decode_responses=True)

# Ensure the Redis Stream consumer group exists before starting the consumer
async def ensure_group():
    try:
        await r.xgroup_create(
            name="post_events",
            groupname="comment_group",
            id="0",
            mkstream=True
        )
        print("Consumer group created!")
    except ResponseError as e:
        if "BUSYGROUP" in str(e):
            print("Consumer group already exists")
        else:
            raise



@app.on_event("startup")
async def startup_event():
    # create Redis stream and consumer group
    await ensure_group()

    # start consumer in background
    asyncio.create_task(consume_post_deleted())