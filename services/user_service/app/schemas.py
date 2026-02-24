from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional

""" input schemas """

# create user (input)
class CreateUserRequest(BaseModel):
    username: str
    password: str
    email: EmailStr
    nickname: str

# update user(input)
class UpdateUserRequest(BaseModel):
    nickname: Optional[str] = None
    image_url: Optional[str] = None

# change email(input)
class ChangeEmailRequest(BaseModel):
    new_email: EmailStr

# verify email(input)
class VerifyEmailRequest(BaseModel):
    token: str

# change password(input)
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


""" output schemas """

# user (output)
class UserResponse(BaseModel):
    id : int
    username: str
    nickname: str
    email: EmailStr
    is_email_verified: bool
    pending_email : Optional[str] = None
    email_verify_token : Optional[str] = None
    email_verify_expire : Optional[datetime] = None
    image_url: Optional[str] = None
    created_at : datetime
    updated_at : datetime
    role : str

    model_config = ConfigDict(from_attributes=True)

# user (output)
class ProfileUserResponse(BaseModel):
    id : int
    nickname: str
    is_email_verified: bool
    pending_email : Optional[str] = None
    image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# user (output)
class PublicUserResponse(BaseModel):
    id : int
    nickname: str
    image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# token (output)
class Token(BaseModel):
    access_token: str
    token_type: str
