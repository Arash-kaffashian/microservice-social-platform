from sqlalchemy import Column, Integer, String, DateTime, func, Boolean

from .database import Base


"""
ORM one model named User then
- use it as admins
- use it as superadmin
by setting one Column named role
"""


# base User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False, unique=True)
    nickname = Column(String(100), nullable=False)
    hashed_password = Column(String)
    email = Column(String(100), nullable=False, index=True)

    is_email_verified = Column(Boolean, default=False)
    pending_email = Column(String(100), nullable=True)
    email_verify_token = Column(String(255), nullable=True)
    email_verify_expire = Column(DateTime, nullable=True)

    role = Column(String, default="user")

    image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

