from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from ..core.rate_limit import rate_limiter


""" limit entire APIs max request per minutes by configure this middleware """


# limit entire APIs max request per minutes
class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ip = request.client.host if request.client else "unknown"
        path = request.url.path

        # bypassing swagger or openapi to use our APIs limitless
        if path.startswith("/docs") or path.startswith("/openapi"):
            return await call_next(request)

        allowed = rate_limiter.is_allowed(
            key=f"global:{ip}",
            limit=1000,
            window=60
        )

        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="Too many requests (global limit)"
            )

        return await call_next(request)

