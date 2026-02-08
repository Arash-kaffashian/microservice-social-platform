from datetime import timedelta, datetime
from passlib.context import CryptContext
from decouple import config
from jose import jwt

from ..models import User


""" authentication and authorization definitions"""


# secret key and algorithm configuration for preventing information hijack
SECRET_KEY = config("SECRET_KEY")
ALGORITHM = config("ALGORITHM")

# encrypt passwords to hashed passwords
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# check user username and password for login
def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    # check the hashed received password with database hashed password
    if not bcrypt_context.verify(password, user.hashed_password):
        return None
    return user

# create and return access token for login authorization
def create_access_token(username: str, user_id: int, expire_delta: timedelta, role: str, is_email_verified: bool):
    # marking token owner and token expire time in payload
    payload = {
        "sub": username,
        "id": user_id,
        "role": role,
        "is_verified": is_email_verified,
        "exp": datetime.utcnow() + expire_delta
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# encrypting normal password into hashed password
def hash_password(password: str):
    return bcrypt_context.hash(password)

# decrypting hashed password into normal password
def verify_password(plain: str, hashed: str):
    return bcrypt_context.verify(plain, hashed)
