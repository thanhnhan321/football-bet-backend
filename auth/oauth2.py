from fastapi.param_functions import Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from datetime import datetime, timedelta
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
from sqlalchemy.orm import Session
from database.database import get_db
from fastapi import HTTPException, status
from database import db_user
from database.models import DbRole, DbUser, DbUserRole

oauth2_scheme_access = OAuth2PasswordBearer(tokenUrl="login")
oauth2_scheme_refresh = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "77407c7339a6c00544e51af1101c4abb4aea2a31157ca5f7dfd87da02a628107"
ALGORITHM = "HS256"


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=10)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    access_token: str = Depends(oauth2_scheme_access), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực thông tin đăng nhập",
        headers={"WWW-Authenticate": "Bearer"},
    )

    expired_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Access token đã hết hạn",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise expired_exception
    except JWTError:
        raise credentials_exception

    user = db_user.get_user_by_username(db, username)

    return user


def get_current_user_roles(
    current_user: DbUser = Depends(get_current_user), db: Session = Depends(get_db)
):
    user_roles = (
        db.query(DbRole)
        .join(DbUserRole, DbRole.id == DbUserRole.role_id)
        .filter(DbUserRole.user_id == current_user.id)
        .all()
    )
    return user_roles
