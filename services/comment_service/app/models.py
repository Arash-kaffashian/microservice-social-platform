from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


""" comments models """


# comment base model
class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, nullable=False)
    post_id = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    parent = relationship(
        "Comment",
        remote_side=[id],
        back_populates="replies"
    )

    replies = relationship(
        "Comment",
        back_populates="parent",
        cascade="all, delete-orphan"
    )
