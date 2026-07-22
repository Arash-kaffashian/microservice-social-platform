from fastapi import HTTPException, Header, Depends, status
from jose import JWTError, jwt
from decouple import config


""" dependencies and permission check """


# config secret key and algorithm based on .env file to prevent information hijack
SECRET_KEY = config("SECRET_KEY")
ALGORITHM = config("ALGORITHM")

# config internal token for internal api calls
INTERNAL_TOKEN = config("INTERNAL_SERVICE_TOKEN")

# decode jwt token and return payload
def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )

    token = authorization.removeprefix("Bearer ")

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    required_claims = (
        "id",
        "sub",
        "nickname",
        "role",
        "is_verified",
    )

    if not all(payload.get(claim) is not None for claim in required_claims):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    return {
        "user_id": payload["id"],
        "username": payload["sub"],
        "nickname": payload["nickname"],
        "role": payload["role"],
        "is_email_verified": payload["is_verified"],
    }

# verified access permission check
def verified_user_required(user = Depends(get_current_user)):
    if not user["is_email_verified"]:
        raise HTTPException(
            status_code=403,
            detail="Email not verified"
        )
    return user
