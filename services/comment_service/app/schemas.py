from pydantic import BaseModel
from datetime import datetime
from typing import Optional


""" comments input/output schemas """


""" input schemas """
# create comment(input)
class CreateComment(BaseModel):
    post_id:int
    content:str

# create reply(input)
class CreateReply(BaseModel):
    post_id:int
    content:str
    parent_id:int

# update comment(input)
class UpdateComment(BaseModel):
    content:str


""" output schemas """
# comment and reply (output)
class CommentResponse(BaseModel):
    id:int
    owner_id:int
    post_id:int
    content:str
    parent_id:Optional[int] = None
    created_at:datetime

