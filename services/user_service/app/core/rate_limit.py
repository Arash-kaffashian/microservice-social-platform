from fastapi import Depends, HTTPException, Request
from collections import defaultdict
import time


""" we have to limit our api calls to prevent the spam attacks or abuse """


# rate limiter class for calculate limit and is_allowed for api calls
class RateLimiter:
    def __init__(self):
        self.storage = defaultdict(list)

    def is_allowed(self, key: str, limit: int, window: int) -> bool:

        now = time.time()
        timestamps = self.storage[key]

        # clear old calls
        self.storage[key] = [t for t in timestamps if now - t < window]

        if len(self.storage[key]) >= limit:
            return False

        self.storage[key].append(now)
        return True


# rate limit definition for dependencies usage to limit api calls
def rate_limit(limit: int, window: int):
    async def dependency(request: Request):
        ip = request.client.host if request.client else "unknown"
        method = request.method

        user_id = getattr(request.state, "user_id", None)

        key = (
            f"user:{user_id}:{method}:{request.url.path}"
            if user_id
            else f"ip:{ip}:{method}:{request.url.path}"
        )

        if not rate_limiter.is_allowed(key, limit, window):
            raise HTTPException(
                status_code=429,
                detail="Too many requests"
            )

    return Depends(dependency)


rate_limiter = RateLimiter()
