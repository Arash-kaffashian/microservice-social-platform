from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session
import uuid
import os

from .. import models


""" Avatar crud """


# media root path setting
MEDIA_ROOT = "media/avatars"

# read one avatar by owner_id
def read_avatar(db: Session, owner_id: int):
    db_avatar = db.query(models.Avatar).filter(
        models.Avatar.owner_id == owner_id
    ).first()

    if not db_avatar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="avatar not found"
        )

    return db_avatar

# create avatar database record for new users
def create_avatar_record(db: Session, owner_id: int):
    db_avatar = db.query(models.Avatar).filter(
        models.Avatar.owner_id == owner_id
    ).first()

    if db_avatar:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="avatar already exist"
        )

    # ✅ فقط اسم فایل ذخیره میشه
    avatar = models.Avatar(
        owner_id=owner_id,
        url="default-avatar.jpg"
    )

    db.add(avatar)
    db.commit()
    db.refresh(avatar)

    return avatar

# set default avatar
async def set_default(db: Session, owner_id: int):
    db_avatar = db.query(models.Avatar).filter(
        models.Avatar.owner_id == owner_id
    ).first()

    if not db_avatar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="owner record not found"
        )
    db_avatar.url = "default-avatar.jpg"

    db.commit()
    db.refresh(db_avatar)

    return db_avatar

# update avatar to new avatar
async def update_avatar(db: Session, owner_id: int, file: UploadFile):

    avatar = db.query(models.Avatar).filter(
        models.Avatar.owner_id == owner_id
    ).first()

    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")

    # new file name
    file_extension = file.filename.split(".")[-1]
    new_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(MEDIA_ROOT, new_filename)

    # save new file
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # delete old file if it was not default avatar
    if avatar.url and avatar.url != "default-avatar.jpg":
        old_path = os.path.join(MEDIA_ROOT, avatar.url)
        if os.path.exists(old_path):
            os.remove(old_path)

    # save new avatar file name to record
    avatar.url = new_filename

    db.commit()
    db.refresh(avatar)

    return avatar

# delete avatar
def delete_avatar(db: Session, owner_id: int):
    db_avatar = db.query(models.Avatar).filter(
        models.Avatar.owner_id == owner_id
    ).first()

    if not db_avatar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avatar not found"
        )

    # delete old file if it was not default avatar
    if db_avatar.url and db_avatar.url != "default-avatar.jpg":
        file_path = os.path.join(MEDIA_ROOT, db_avatar.url)
        if os.path.exists(file_path):
            os.remove(file_path)

    db.delete(db_avatar)
    db.commit()

    return {"detail": "Avatar successfully deleted"}