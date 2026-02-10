from fastapi import FastAPI, Depends, HTTPException, APIRouter, status
from sqlalchemy.orm import Session

from .. import schemas, database, dependencies
from ..crud import comments


""" comments routers """


router = APIRouter()

# get one post all comments limited list
@router.get("/comments/{post_id}", response_model=list[schemas.CommentResponse])
def read_comments(
        post_id:int,
        skip: int = 0,
        limit: int = 10,
        db: Session = Depends(database.get_db)
):
    return comments.read_comments(db, post_id, skip, limit)

# get one comment all replies limited list
@router.get("/comments/replies/{comment_id}", response_model=list[schemas.CommentResponse])
def read_replies(
        comment_id:int,
        skip: int = 0,
        limit: int = 10,
        db: Session = Depends(database.get_db)
):
    return comments.read_replies(db, comment_id, skip, limit)

# create my comment
@router.post("/comments", response_model=schemas.CommentResponse)
def create_comment(
        comment: schemas.CreateComment,
        db: Session = Depends(database.get_db),
        user=Depends(dependencies.verified_user_required)
):
    owner_id = user["user_id"]
    return comments.create_reply_comment(db, comment, owner_id)

# update one comment/reply by id
@router.patch("/comments/{comment_id}", response_model=schemas.CommentResponse)
def update_comment(
        comment: schemas.UpdateComment,
        comment_id:int,
        db: Session = Depends(database.get_db),
        user=Depends(dependencies.verified_user_required)
):
    owner_id = user["user_id"]
    return comments.update_comment(db, comment_id, comment, owner_id)

# delete one comment and its replies by id
@router.delete("/comments/delete/{comment_id}", status_code=status.HTTP_200_OK)
def delete_comment(
        comment_id:int,
        db: Session = Depends(database.get_db),
        user=Depends(dependencies.verified_user_required)
):
    owner_id = user["user_id"]
    return comments.delete_my_comment(db, comment_id, owner_id)
