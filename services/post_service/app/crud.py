from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from . import models, schemas


""" posts crud """


# return limited list from all posts
def get_posts(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Post).offset(skip).limit(limit).all()

# return limited list from all of my posts
def get_my_posts(db: Session, owner_id: int, skip: int = 0, limit: int = 10):
    return (
        db.query(models.Post)
        .filter(models.Post.owner_id == owner_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

# return one post by id
def get_post(db: Session, post_id: int):
    return db.query(models.Post).filter(models.Post.id == post_id).first()

# create one post and commit it to db
def create_post(db: Session, post: schemas.PostCreate, user:int):
    db_post = models.Post(
        title=post.title,
        content=post.content,
        owner_id=user,
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

# update one post by id and commit it to db
def update_post(db: Session, post_id: int, patch: schemas.PostUpdate):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not db_post:
        return None

    # detect and update every object that writen in patch and only them
    for field, value in patch.dict(exclude_unset=True).items():
        setattr(db_post, field, value)

    db.commit()
    db.refresh(db_post)
    return db_post

# delete one post by id and commit it to db
def delete_post(db: Session, post_id: int):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")
    db.delete(db_post)
    db.commit()
    return "post successfully deleted"

# delete one user posts by user_id and commit it to db
def delete_user_posts(db: Session, user_id: int):
    posts = db.query(models.Post).filter(models.Post.owner_id == user_id).all()

    deleted_posts = []

    for post in posts:
        deleted_posts.append(post)
        db.delete(post)

    db.commit()

    return deleted_posts
