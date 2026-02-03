from fastapi import FastAPI

from .middleware.rate_limit import RateLimitMiddleware
from . import models, database
from .routers import auth, user, account, admin
from .database import SessionLocal
from .crud.admin import create_superadmin


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

# superadmin create or promote on startup
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        create_superadmin(db)
    finally:
        db.close()
