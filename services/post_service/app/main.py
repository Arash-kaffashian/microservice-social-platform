from fastapi import FastAPI

from . import models, database
from .routers import posts


models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Post Service")

app.include_router(posts.router)




