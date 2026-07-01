from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Any, Optional


""" notifications input/output schemas """


""" input schemas """
# payload (input)
class NotificationPayloadData(BaseModel):
    model_config = ConfigDict(extra='allow')
    message: str

# notification for admin (input)
class NotificationInput(BaseModel):
    recipient_id: Optional[int] = None
    actor_id: int
    type: str
    object_type: Optional[str] = None
    object_id: Optional[int] = None
    expire_days: Optional[int] = None
    payload: Optional[NotificationPayloadData] = None
    is_public: bool = False

# create notification (input)
class CreateNotificationInput(BaseModel):
    recipient_id: Optional[int] = None
    message: str
    is_public: Optional[bool] = False

# update notification (input)
class UpdateNotificationInput(BaseModel):
    message: str


""" output schemas """
# notification (output)
class NotificationSchema(BaseModel):
    id: int
    recipient_id: Optional[int] = None
    actor_id: Optional[int] = None
    type: str
    object_type: Optional[str] = None
    object_id: Optional[int] = None
    read_at: Optional[datetime] = None
    created_at: datetime
    expires_at: datetime
    payload: Optional[Any] = None
    is_public: bool

    model_config = ConfigDict(from_attributes=True)

# notification (output)
class NotificationResponse(BaseModel):
    id:int
    recipient_id:int
    type:str
    is_public:bool
    created_at:datetime
    payload:NotificationPayloadData

# pagination meta schema (meta)
class MetaSchema(BaseModel):
    total: int
    skip: int
    limit: int

# pagination notification schema (output)
class PaginatedNotificationResponse(BaseModel):
    items: list[NotificationSchema]
    meta: MetaSchema
