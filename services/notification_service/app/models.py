from sqlalchemy import Column, String, DateTime, Boolean, Integer, Index, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from datetime import datetime, timezone
import uuid

from .database import Base


""" Notification models """


# notification base model (public and private)
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)

    recipient_id = Column(Integer, nullable=True, index=True)
    actor_id = Column(Integer, nullable=True)

    type = Column(String, nullable=False)

    object_type = Column(String, nullable=True)
    object_id = Column(Integer, nullable=True)

    read_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False,default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)

    payload = Column(JSON, nullable=True)

    is_public = Column(Boolean, nullable=False, default=False)

    __table_args__ = (
        Index("ix_notifications_recipient_created", "recipient_id", "created_at"),
        Index("ix_notifications_recipient_read", "recipient_id", "read_at"),
        Index("ix_notifications_type", "type"),
        Index("ix_notifications_object", "object_type", "object_id"),
    )