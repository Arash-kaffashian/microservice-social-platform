from fastapi import HTTPException

from .. import crud
from ..events.publisher import publish_post_deleted


""" router and crud bridge """


# bridge between router and crud to publish post_deleted for other services
async def delete_post(db, post_id: int):
    post = crud.delete_post(db, post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    await publish_post_deleted(post_id)

    return {"detail": "Post deleted successfully"}
