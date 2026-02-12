from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas


""" comments crud """


# get one post all comments/replies
def read_comments(db: Session, post_id, skip: int = 0, limit: int = 10):
    return db.query(models.Comment).filter(models.Comment.post_id == post_id).offset(skip).limit(limit).all()

# get one comment all replies
def read_replies(db: Session, comment_id, skip: int = 0, limit: int = 10):
    return db.query(models.Comment).filter(models.Comment.parent_id == comment_id).offset(skip).limit(limit).all()

# create one comment for one post
def create_comment(db: Session, comment: schemas.CreateComment, user:int):
    db_comment = models.Comment(
        owner_id=user,
        post_id=comment.post_id,
        content=comment.content,
        parent_id=None,
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

# create one reply for one comment
def create_reply_comment(db: Session, comment: schemas.CreateReply, user:int):
    db_reply = db.query(models.Comment).filter(models.Comment.id == comment.parent_id).first()
    if not db_reply :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Parent comment not found")
    if not db_reply.post_id == comment.post_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="reply and comment post_id are not match!")

    db_comment = models.Comment(
        owner_id=user,
        post_id=comment.post_id,
        content=comment.content,
        parent_id=comment.parent_id,
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

# update one comment context by id
def update_comment(db: Session, comment_id, comment: schemas.UpdateComment, user:int):
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not db_comment :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="comment not found")

    if not db_comment.owner_id == user :
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="only comment owner can update that")

    # detect and update every object that writen in patch and only them
    for field, value in comment.dict(exclude_unset=True).items():
        setattr(db_comment, field, value)

    db.commit()
    db.refresh(db_comment)
    return db_comment

# delete one comment and all of its replies by id
def delete_my_comment(db: Session, comment_id: int, owner_id:int):
    db_user = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="comment not found")
    if not db_user.owner_id == owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="only comment owner can delete that")
    db.delete(db_user)
    db.commit()
    return {"detail": "Your comment has been deleted"}

# delete one post all comments and its replies by post_id
def delete_post_comments(db: Session, post_id: int):
    db.query(models.Comment)\
      .filter(models.Comment.post_id == post_id)\
      .delete(synchronize_session=False)

    db.commit()
