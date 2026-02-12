from fastapi import FastAPI, Depends, HTTPException, APIRouter, status
from sqlalchemy.orm import Session

from .. import schemas, crud, database, dependencies
from ..services import post_service


""" posts routers """


router = APIRouter()

# get all posts limited list
@router.get("/posts", response_model=list[schemas.PostResponse])
def read_posts(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    return crud.get_posts(db, skip, limit)

# get all my posts limited list
@router.get("/myposts/", dependencies=[Depends(dependencies.verified_user_required)], response_model=list[schemas.PostResponse])
def read_my_posts(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db), user=Depends(dependencies.get_current_user)):
    owner_id = user["user_id"]
    return crud.get_my_posts(db, owner_id, skip, limit)

# get one post by id
@router.get("/posts/{post_id}", response_model=schemas.PostResponse)
def read_post(post_id: int, db: Session = Depends(database.get_db)):
    db_post = crud.get_post(db, post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post

# create my post
@router.post("/posts", dependencies=[Depends(dependencies.get_current_user), Depends(dependencies.verified_user_required)], response_model=schemas.PostResponse)
def create_post(post: schemas.PostCreate, db: Session = Depends(database.get_db), user=Depends(dependencies.get_current_user)):
    owner_id = user["user_id"]
    return crud.create_post(db, post, owner_id)

# update one of my posts by id
@router.patch("/posts/{post_id}", response_model=schemas.PostResponse)
def update_post(patch: schemas.PostUpdate, post_id: int, db : Session = Depends(database.get_db), user=Depends(dependencies.get_current_user)):
    post = crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="post not found")
    if post.owner_id != user["user_id"]:
        raise HTTPException(status_code=403, detail="only post owner can update that")
    db_post = crud.update_post(db, post_id, patch)
    return db_post

# delete one of my posts by id
@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db : Session = Depends(database.get_db), user=Depends(dependencies.get_current_user)):
    post = crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="post not found")
    if post.owner_id != user["user_id"]:
        raise HTTPException(status_code=403, detail="only post owner can delete that")
    return await post_service.delete_post(db, post_id)

# delete one post by id (admin and superadmin only)
@router.delete("/admin/posts/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post_by_admin(post_id: int, db : Session = Depends(database.get_db), user=Depends(dependencies.get_current_user)):
    post = crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="post not found")
    if user["role"] not in ("admin", "superadmin"):
        raise HTTPException(status_code=403, detail="admin access required")
    return await post_service.delete_post(db, post_id)
