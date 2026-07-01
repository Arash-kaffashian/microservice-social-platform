from sqlalchemy import Column, Integer, String, Text, DateTime, func, ARRAY

from .database import Base


""" posts models """


# post base model
class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50), nullable=False)
    content = Column(Text, nullable=False, max_length=255)
    owner_id = Column(Integer, nullable=False)
    owner_nickname = Column(String(50), nullable=False)
    media_urls = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
