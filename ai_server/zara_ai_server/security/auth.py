import time
from collections import defaultdict, deque
from fastapi import Depends, Header, HTTPException, Request, status
import jwt
from zara_ai_server.config import Settings, get_settings

_hits: dict[str, deque[float]] = defaultdict(deque)

def authenticate(
    request: Request,
    authorization: str = Header(default=""),
    settings: Settings = Depends(get_settings),
) -> dict:
    if settings.local_testing:
        return {"sub": "local-test-device", "mode": "local"}
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    try:
        claims = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"], options={"require": ["sub"]})
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token") from exc
    client_key = f"{claims.get('sub')}:{request.client.host if request.client else 'unknown'}"
    now = time.monotonic()
    bucket = _hits[client_key]
    while bucket and now - bucket[0] > 60:
        bucket.popleft()
    if len(bucket) >= settings.request_rate_per_minute:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="rate limit exceeded")
    bucket.append(now)
    return claims
