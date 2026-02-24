from pydantic import BaseModel, ConfigDict
from datetime import datetime


""" media input/output schemas """


""" output schemas """
# avatar (output)
class AvatarResponse(BaseModel):
    id:int
    url:str
    created_at:datetime
    updated_at:datetime

# avatar (output)
class MediaResponse(BaseModel):
    id:int
    url:str
    created_at:datetime
    updated_at:datetime

    model_config = ConfigDict(from_attributes=True)