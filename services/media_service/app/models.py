from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
import enum

from .database import Base


""" media models """


class MediaType(str, enum.Enum):
    image = "image"
    video = "video"

# media base model
class Media(Base):
    __tablename__ = "Medias"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, nullable=False)
    owner_id = Column(Integer, nullable=False)
    url = Column(String, nullable=False)
    media_type = Column(Enum(MediaType, name="media_type_enum"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# avatar base model
class Avatar(Base):
    __tablename__ = "Avatars"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, nullable=False, unique=True)
    url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
