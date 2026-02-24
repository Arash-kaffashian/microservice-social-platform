from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session
import uuid
import os

from .. import models


""" Media crud """


# media root setting
MEDIA_ROOT = "media/medias"

# read media by id
def read_media(db: Session, media_id:int):
    db_media = db.query(models.Media).filter(models.Media.id == media_id).first()
    if not db_media:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="media not found")
    return db_media

# read medias by post_id
def read_medias(db: Session, post_id:int):
    db_media = db.query(models.Media).filter(models.Media.post_id == post_id).all()
    if not db_media:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="there is no media for this post")
    return db_media

# save and create media
def create_media(db: Session, post_id: int, owner_id:int, file: UploadFile):

    # check file type
    content_type = file.content_type

    if content_type.startswith("image"):
        media_type = "image"
    elif content_type.startswith("video"):
        media_type = "video"
    else:
        raise HTTPException(status_code=400, detail="Unsupported media type")

    # create uuid file name
    file_extension = file.filename.split(".")[-1]
    new_filename = f"{uuid.uuid4()}.{file_extension}"

    upload_dir = os.path.join(MEDIA_ROOT)
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, new_filename)

    try:
        # save file
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        # create database record
        db_media = models.Media(
            post_id=post_id,
            owner_id=owner_id,
            url=new_filename,
            media_type=media_type
        )

        db.add(db_media)
        db.commit()
        db.refresh(db_media)

        return db_media

    except Exception as e:
        db.rollback()

        # اگر فایل ذخیره شده بود، پاکش کن
        if os.path.exists(file_path):
            os.remove(file_path)

        raise HTTPException(status_code=500, detail="Media creation failed")

# update media
async def update_media(db: Session, media_id: int, user_id:int, file: UploadFile):

    media = db.query(models.Media).filter(models.Media.id == media_id).first()

    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    if media.owner_id != user_id:
        raise HTTPException(status_code=403, detail="You are not allowed to update this media")

    # check file type
    content_type = file.content_type

    if content_type.startswith("image"):
        media_type = "image"
    elif content_type.startswith("video"):
        media_type = "video"
    else:
        raise HTTPException(status_code=400, detail="Only image or video files are allowed")

    # create new uuid file name
    file_extension = file.filename.split(".")[-1]
    new_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(MEDIA_ROOT, new_filename)

    # save new file
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # remove old file
    if media.url:
        old_path = os.path.join(MEDIA_ROOT, media.url)
        if os.path.exists(old_path):
            os.remove(old_path)

    # update database record
    media.url = new_filename
    media.media_type = media_type

    db.commit()
    db.refresh(media)

    return media

def delete_media(db: Session, media_id: int, user_id:int):
    db_media = db.query(models.Media).filter(models.Media.id == media_id).first()

    if not db_media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found"
        )

    if db_media.owner_id != user_id:
        raise HTTPException(status_code=403, detail="You are not allowed to delete this media")

    # remove file
    if db_media.url:
        file_path = os.path.join(MEDIA_ROOT, db_media.url)

        if os.path.exists(file_path):
            os.remove(file_path)

    # delete record
    db.delete(db_media)
    db.commit()

    return {"detail": "Media successfully deleted"}

# delete one post medias by post_id and commit it to db
def delete_post_medias(db: Session, post_id: int):
    db.query(models.Media).filter(models.Media.post_id == post_id).delete(synchronize_session=False)
    db.commit()
