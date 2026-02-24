from fastapi import FastAPI
from redis.exceptions import ResponseError
from decouple import config
import redis.asyncio as redis
import asyncio

from .middleware.rate_limit import RateLimitMiddleware
from .events.consumer import consume_avatar_updated
from . import models, database
from .routers import auth, user, account, admin
from .database import SessionLocal
from .services.admin_service import create_superadmin


# sqlalchemy engine setting
models.Base.metadata.create_all(bind=database.engine)

# fastapi setting
app = FastAPI(title="User service")

# middlewares setting
app.add_middleware(RateLimitMiddleware)

# routers setting
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(account.router)
app.include_router(admin.router)

# fastapi dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


r = redis.Redis(host=config("HOST"), port=config("PORT"), decode_responses=True)

# Ensure the Redis Stream consumer group exists before starting the consumer
async def ensure_group():
    try:
        await r.xgroup_create(
            name="media_events",
            groupname="user_group",
            id="0",
            mkstream=True
        )
        print("Consumer group created!")
    except ResponseError as e:
        if "BUSYGROUP" in str(e):
            print("Consumer group already exists")
        else:
            raise

# superadmin create or promote on startup / redis group Ensure
@app.on_event("startup")
async def startup_event():
    # Create superadmin
    db = SessionLocal()
    try:
        await create_superadmin(db)
    finally:
        db.close()

    # Ensure Redis group exists
    await ensure_group()

    # Start consumer in background
    asyncio.create_task(consume_avatar_updated())
