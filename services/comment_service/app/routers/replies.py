from fastapi import FastAPI, Depends, HTTPException, APIRouter, status
from sqlalchemy.orm import Session

from .. import schemas, database, dependencies
from ..services import replies_service


""" replies routers """


router = APIRouter()

# create my reply on one comment
@router.post(
    "/comments/reply",
    dependencies=[Depends(dependencies.get_current_user)],
    response_model=schemas.CommentResponse
)
async def create_relpy(
        comment: schemas.CreateReply,
        db: Session = Depends(database.get_db),
        user=Depends(dependencies.get_current_user)
):
    owner_id = user["user_id"]
    owner_nickname = user["nickname"]
    return await replies_service.create_reply(db, comment, owner_id, owner_nickname)
