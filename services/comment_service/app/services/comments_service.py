from fastapi import HTTPException, status

from ..crud import comments
from ..schemas import CreateComment
from ..events.publisher import publish_comment_created


""" router and crud bridge """


# bridge between router and crud to publish_comment_created for other services
async def create_comment(db, comment_data: CreateComment, owner_id, owner_nickname):
    db_user = comments.create_comment(db, comment_data, owner_id, owner_nickname)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="something went wrong!")

    await publish_comment_created(db_user.id, db_user.owner_id, db_user.nickname, db_user.post_id)
    return db_user
