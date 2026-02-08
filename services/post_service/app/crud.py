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
        image_url=post.image_url,
        video_url=post.video_url,
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
def delete_post(db: Session, post_id: int) -> bool:
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not db_post:
        return False
    db.delete(db_post)
    db.commit()
    return None

