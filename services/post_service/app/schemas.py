from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# input api form
class PostCreate(BaseModel):
    title: str
    content: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None

# output api form
class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True
