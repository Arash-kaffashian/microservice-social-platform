from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer

from . import models, database
from .routers import comments, replies


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

models.Base.metadata.create_all(bind=database.engine)

# FastAPI app config
app = FastAPI(title="Comment Service")

# include routers
app.include_router(comments.router)
app.include_router(replies.router)
