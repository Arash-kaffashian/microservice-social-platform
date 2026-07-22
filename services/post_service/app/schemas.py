from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List


""" posts input/output schemas """


""" input api form"""
# create post
class PostCreate(BaseModel):
    title: str
    content: str
    media_urls: Optional[List[str]] = None

# update post
class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    media_urls: Optional[List[str]] = None

# notification (input)
class NotificationInput(BaseModel):
    post_id: int
    post_owner: int
    owner_id: int
    owner_nickname: str
    comment_id: int


""" output api form"""
# post all details
class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    owner_id: int
    owner_nickname: str
    media_urls: Optional[List[str]] = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
