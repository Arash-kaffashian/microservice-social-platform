from pydantic import BaseModel
from datetime import datetime
from typing import Optional


""" posts input/output schemas """


""" input api form"""
# create post
class PostCreate(BaseModel):
    title: str
    content: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None

# update post
class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None

""" output api form"""
# post all details
class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    owner_id: int
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True
