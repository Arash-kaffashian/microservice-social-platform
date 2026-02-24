from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from typing import List
import os

from ..database import get_db
from .. import schemas, dependencies
from ..crud import media_crud


""" Media routers """


# router prefix and tag config
router = APIRouter(prefix="/files", tags=["Media"])

# avatar upload path setup
UPLOAD_DIR = "media"

# makedirs if its not exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

# get one post all medias
@router.get("/post={post_id}", response_model=List[schemas.MediaResponse])
async def get_post_medias(post_id:int, db: Session = Depends(get_db)):
    return media_crud.read_medias(db, post_id)

# get one media by id
@router.get("/media={media_id}", response_model=schemas.MediaResponse)
async def get_media_by_id(media_id:int, db: Session = Depends(get_db)):
    return media_crud.read_media(db, media_id)

# upload media and create a record for it
@router.post("/upload")
async def upload_file(post_id: int, files: List[UploadFile] = File(...), user = Depends(dependencies.get_current_user), db: Session = Depends(get_db)):
    urls = []

    for file in files:
        media = media_crud.create_media(db, post_id=post_id, file=file, owner_id=user["user_id"])
        urls.append(media.url)

    return {"urls": urls}

# change one media record and file by id
@router.patch("/media={media_id}", dependencies=[Depends(dependencies.internal_service_required)], response_model=dict)
async def update_file(media_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), user = Depends(dependencies.get_current_user)):
    media = await media_crud.update_media(db, media_id=media_id, user_id=user["user_id"], file=file)
    return {"url": media.url}

# delete one media by id
@router.delete("/media={media_id}", dependencies=[Depends(dependencies.internal_service_required)])
async def delete_file (media_id:int, db:  Session = Depends(get_db), user = Depends(dependencies.get_current_user)):
    return media_crud.delete_media(db, media_id, user_id=user["user_id"])
