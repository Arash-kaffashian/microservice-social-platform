from fastapi import FastAPI, Depends, HTTPException, APIRouter, status
from .. import models, schemas, crud, database
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/posts", response_model=schemas.PostResponse)
def create_post(post: schemas.PostCreate, db: Session = Depends(database.get_db)):
    return crud.create_post(db, post)

@router.get("/posts/{post_id}", response_model=schemas.PostResponse)
def read_post(post_id: int, db: Session = Depends(database.get_db)):
    db_post = crud.get_post(db, post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post

@router.get("/posts", response_model=list[schemas.PostResponse])
def read_posts(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    return crud.get_posts(db, skip, limit)

@router.patch("/posts/{post_id}", response_model=schemas.PostResponse)
def update_post(patch: schemas.PostUpdate, post_id: int, db : Session = Depends(database.get_db)):
    db_post = crud.update_post(db, post_id, patch)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post

@router.patch("/posts/{post_id}", response_model=schemas.PostResponse)
def update_post(patch: schemas.PostUpdate, post_id: int, db : Session = Depends(database.get_db)):
    db_post = crud.update_post(db, post_id, patch)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post

@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db : Session = Depends(database.get_db)):
    db_post = crud.delete_post(db, post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail=f"{post_id} has been deleted!")
    return db_post