from fastapi import HTTPException, status

from ..crud import comments
from ..schemas import CreateReply
from ..events.publisher import publish_reply_created


""" router and crud bridge """


# bridge between router and crud to publish_reply_created for other services
async def create_reply(db, reply_data: CreateReply, owner_id, owner_nickname):
    db_reply, parent_owner_id = comments.create_reply_comment(db, reply_data, owner_id, owner_nickname)
    if not db_reply:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="something went wrong!")

    await publish_reply_created(
        db_reply.id,
        db_reply.owner_id,
        db_reply.nickname,
        db_reply.parent_id,
        parent_owner_id,
        db_reply.post_id
    )

    return db_reply
