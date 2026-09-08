from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status
from pydantic import BaseModel

from .config import get_settings


class TokenRequest(BaseModel):
    email: str


def issue_token(email: str) -> str:
    settings = get_settings()
    return jwt.encode({"sub": email, "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)}, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def require_token(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required")
    try:
        return jwt.decode(authorization[7:], get_settings().jwt_secret, algorithms=[get_settings().jwt_algorithm])["sub"]
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc
