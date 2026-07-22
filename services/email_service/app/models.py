from sqlalchemy import Column, Integer, String, DateTime, func, Boolean

from .database import Base


""" Emails models """


# email base model
class EmailVerification(Base):
    __tablename__ = "EmailVerifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, unique=True)

    email = Column(String(100), nullable=False)
    token = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default = False, nullable=False)

    expire_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
