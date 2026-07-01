from fastapi import HTTPException

from .. import crud, schemas
from ..events import publisher


""" router and crud bridge """


# create post service for publishing post_created
async def create_post(db, post: schemas.PostCreate, owner_id:int, nickname:str):
    db_post = crud.create_post(db, post, owner_id, nickname)
    if not db_post:
        raise HTTPException(status_code=400, detail="bad request")
    await publisher.publish_post_created(db_post.id, db_post.owner_id, db_post.title, db_post.owner_nickname)
    print("published")
    return db_post

# bridge between router and crud to publish post_deleted for other services
async def delete_post(db, post_id: int):
    crud.delete_post(db, post_id)

    await publisher.publish_post_deleted(post_id)

    return
