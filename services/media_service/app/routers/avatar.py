from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
import os

from .. import schemas, dependencies
from ..services import avatar_service
from ..database import SessionLocal, get_db
from ..crud import avatar_crud


""" Avatar routers """


# router prefix and tag config
router = APIRouter(prefix="/avatar", tags=["Avatar"])

# avatar upload path setup
UPLOAD_DIR = "media/avatars"

# makedirs if its not exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

# get avatar by owner_id
@router.get("/id={owner_id}", dependencies=[Depends(dependencies.internal_service_required)], response_model=schemas.AvatarResponse)
async def read_avatar(owner_id:int, db: Session = Depends(get_db)):
    return  avatar_crud.read_avatar(db,owner_id=owner_id)

# create avatar database record and set it to default
@router.post("/create_record", dependencies=[Depends(dependencies.internal_service_required)], response_model=dict)
async def create_record(owner_id:int, db: Session = Depends(get_db)):
    avatar = avatar_crud.create_avatar_record(db,owner_id=owner_id)
    return {"url": avatar.url}

# change avatar database record to default
@router.put("/set_default", response_model=schemas.AvatarResponse)
async def set_default(user=Depends(dependencies.get_current_user), db: Session = Depends(get_db)):
    avatar = await avatar_service.set_default(db, owner_id=user["user_id"])
    return avatar

# change avatar record and file to new avatar
@router.put("/", response_model=schemas.AvatarResponse)
async def update_avatar(file: UploadFile = File(...),user=Depends(dependencies.get_current_user),db: Session = Depends(get_db)):
    avatar = await avatar_service.avatar_updated(db, owner_id=user["user_id"], file=file)
    return avatar

# delete avatar record and file
@router.delete("/id={owner_id}", dependencies=[Depends(dependencies.internal_service_required)])
async def delete_avatar (owner_id:int, db: Session = Depends(get_db)):
    return avatar_crud.delete_avatar(db, owner_id)
