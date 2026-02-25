from fastapi import APIRouter, HTTPException, status
from fastapi.param_functions import Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from jose.exceptions import JWTError, ExpiredSignatureError
from sqlalchemy.orm.session import Session
from database.database import get_db
from database import models
from database.hash import Hash
from auth import oauth2
from auth.oauth2 import ALGORITHM, SECRET_KEY, oauth2_scheme_refresh
from jose import jwt
from routers.schemas import RefreshToken
from ldap3 import Server, Connection, ALL
from routers.schemas import LoginRequest
import re
import time


router = APIRouter(tags=["authentication"])

ldap_server = "ldap://10.3.12.17"
ldap_port = 389
ldap_server = Server(ldap_server, port=ldap_port, get_info=ALL)


@router.post("/login")
def get_access_token(
    request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    # time.sleep(5)
    user = (
        db.query(models.DbUser)
        .filter(models.DbUser.username == request.username)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Thông tin đăng nhập không hợp lệ!",
        )
    if not Hash.verify(user.password, request.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sai mật khẩu!"
        )

    access_token = oauth2.create_access_token(data={"sub": user.username})
    refresh_token = oauth2.create_refresh_token(data={"sub": user.username})

    role_name = (
        db.query(models.DbRole.role_name)
        .join(models.DbUserRole, models.DbRole.id == models.DbUserRole.role_id)
        .filter(models.DbUserRole.user_id == user.id)
        .first()
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "username": user.username,
        "role_name": role_name[0],
    }


@router.post("/refresh-token")
def get_new_token(request: RefreshToken):
    invalid_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh token không đúng",
        headers={"WWW-Authenticate": "Bearer"},
    )

    expired_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh token đã hết hạn",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise invalid_token_exception
        else:
            access_token = oauth2.create_access_token(data={"sub": username})
            refresh_token = oauth2.create_refresh_token(data={"sub": username})
    except ExpiredSignatureError:
        raise expired_token_exception
    except JWTError:
        raise invalid_token_exception

    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post("/login/ldap")
async def login_for_ldap_account(login_request: LoginRequest):
    if " " in login_request.email:
        raise HTTPException(
            status_code=400, detail="Email không được chứa khoảng trắng"
        )

    if "@" not in login_request.email:
        login_request.email += "@mobifone.vn"

    if not re.match(r"[^@]+@[^@]+\.[^@]+", login_request.email):
        raise HTTPException(status_code=400, detail="Định dạng email không hợp lệ")

    if not login_request.email.endswith("@mobifone.vn"):
        raise HTTPException(
            status_code=400, detail="Vui lòng đăng nhập bằng tài khoản mobifone"
        )

    try:
        with Connection(
            ldap_server,
            user=login_request.email,
            password=login_request.password,
            auto_bind=True,
        ) as conn:
            return HTTPException(
                status_code=status.HTTP_200_OK, detail="Đăng nhập thành công"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Thông tin đăng nhập không hợp lệ",
            headers={"WWW-Authenticate": "Bearer"},
        )
