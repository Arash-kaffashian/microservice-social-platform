from fastapi import FastAPI
from redis.exceptions import ResponseError
from decouple import config
from fastapi_swagger import patch_fastapi
import redis.asyncio as redis
import asyncio

from .middleware.rate_limit import RateLimitMiddleware
from .events.consumer import consume_avatar_events, consume_email_events
from . import models, database
from .routers import auth, user, account, admin
from .database import SessionLocal
from .services.admin_service import create_superadmin


# sqlalchemy engine setting
models.Base.metadata.create_all(bind=database.engine)

# fastapi setting
app = FastAPI(title="User service",docs_url=None,swagger_ui_oauth2_redirect_url=None)
patch_fastapi(app)

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
    streams = ["notification_events", "email_events", "media_events", "comment_events", "post_events"]

    for stream in streams:
        try:
            await r.xgroup_create(
                name=stream,
                groupname="user_group",
                id="0",
                mkstream=True
            )
            print(f"Consumer group created for {stream}")
        except ResponseError as e:
            if "BUSYGROUP" in str(e):
                print(f"Consumer group already exists for {stream}")
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
    asyncio.create_task(consume_avatar_events())
    asyncio.create_task(consume_email_events())
