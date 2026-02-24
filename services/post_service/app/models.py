from sqlalchemy import Column, Integer, String, Text, DateTime, func

from .database import Base


""" posts models """


# post base model
class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    owner_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
