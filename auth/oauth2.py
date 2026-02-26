from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
from sqlalchemy.orm import Session

from core.config import settings
from database import db_user
from database.database import get_db
from database.models import DbRole, DbUser, DbUserRole

oauth2_scheme_access = OAuth2PasswordBearer(tokenUrl="/login")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.jwt_algorithm

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def _create_token(data: dict, expires_minutes: int, token_type: str) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire, "token_type": token_type})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(data: dict) -> str:
    return _create_token(
        data=data,
        expires_minutes=settings.access_token_expire_minutes,
        token_type=ACCESS_TOKEN_TYPE,
    )


def create_refresh_token(data: dict) -> str:
    return _create_token(
        data=data,
        expires_minutes=settings.refresh_token_expire_minutes,
        token_type=REFRESH_TOKEN_TYPE,
    )


def decode_refresh_token(token: str) -> dict:
    return _decode_token(token=token, expected_token_type=REFRESH_TOKEN_TYPE)


def _decode_token(token: str, expected_token_type: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token đã hết hạn",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    if payload.get("token_type") != expected_token_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai loại token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


def get_current_user(
    access_token: str = Depends(oauth2_scheme_access),
    db: Session = Depends(get_db),
):
    payload = _decode_token(token=access_token, expected_token_type=ACCESS_TOKEN_TYPE)
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Không thể xác thực thông tin đăng nhập",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db_user.get_user_by_username(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Không thể xác thực thông tin đăng nhập",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_user_roles(
    current_user: DbUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(DbRole)
        .join(DbUserRole, DbRole.id == DbUserRole.role_id)
        .filter(DbUserRole.user_id == current_user.id)
        .all()
    )
