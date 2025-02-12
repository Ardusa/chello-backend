from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import HTTPException
from constants import AUTH
import uuid

def create_access_token(data: dict):
    expires_delta = timedelta(minutes=AUTH.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"sub": str(data["sub"]), "exp": expire}
    return jwt.encode(to_encode, AUTH.SECRET_KEY, algorithm=AUTH.ALGORITHM)

def create_refresh_token(data: dict):
    expires_delta = timedelta(minutes=AUTH.REFRESH_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"sub": str(data["sub"]), "exp": expire}
    return jwt.encode(to_encode, AUTH.SECRET_KEY, algorithm=AUTH.ALGORITHM)

def decode_jwt(token: str) -> dict:
    """Decode a JWT token and return the payload with the user swapped for a UUID"""
    try:
        payload = jwt.decode(token, AUTH.SECRET_KEY, algorithms=[AUTH.ALGORITHM])
        id: uuid.UUID = uuid.UUID(payload.pop("sub"))
        payload["sub"] = id
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {e}")
