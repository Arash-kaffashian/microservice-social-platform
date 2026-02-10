from fastapi import FastAPI, Depends, HTTPException, APIRouter, status
from sqlalchemy.orm import Session

from .. import schemas, database, dependencies
from ..crud import comments


""" replies routers """


router = APIRouter()

# create my reply on one comment
@router.post(
    "/comments/reply",
    dependencies=[Depends(dependencies.get_current_user)],
    response_model=schemas.CommentResponse
)
def create_relpy(
        post: schemas.CreateReply,
        db: Session = Depends(database.get_db),
        user=Depends(dependencies.get_current_user)
):
    owner_id = user["user_id"]
    return comments.create_reply_comment(db, post, owner_id)
