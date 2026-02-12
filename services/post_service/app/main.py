from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
import redis.asyncio as redis
from decouple import config
import asyncio

from .events.consumer import consume_user_deleted
from . import models, database
from .routers import posts


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Post Service")

app.include_router(posts.router)


r = redis.Redis(host=config("HOST"), port=config("PORT"), decode_responses=True)


# post_service startup for Ensure the Redis Stream consumer group exists before starting the consumer
@app.on_event("startup")
async def startup_event():

    try:
        await r.xgroup_create(
            name="user_events",
            groupname="post_group",
            id="0",
            mkstream=True
        )
    except Exception:
        pass

    await asyncio.create_task(consume_user_deleted())
