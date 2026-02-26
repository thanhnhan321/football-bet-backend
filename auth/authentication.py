import re

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from ldap3 import ALL, Connection, Server
from sqlalchemy.orm import Session

from auth import oauth2
from core.config import settings
from database import models
from database.database import get_db
from database.hash import Hash
from routers.schemas import LoginRequest, RefreshToken

router = APIRouter(tags=["authentication"])

ldap_server = Server(
    settings.ldap_server_url,
    port=settings.ldap_server_port,
    get_info=ALL,
)


@router.post("/login")
def get_access_token(
    request: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = (
        db.query(models.DbUser)
        .filter(models.DbUser.username == request.username)
        .first()
    )

    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Thông tin đăng nhập không hợp lệ",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not user or not Hash.verify(user.password, request.password):
        raise invalid_credentials

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
        "role_name": role_name[0] if role_name else "member",
    }


@router.post("/refresh-token")
def get_new_token(request: RefreshToken):
    payload = oauth2.decode_refresh_token(request.refresh_token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token không hợp lệ",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": oauth2.create_access_token(data={"sub": username}),
        "refresh_token": oauth2.create_refresh_token(data={"sub": username}),
    }


@router.post("/login/ldap")
async def login_for_ldap_account(login_request: LoginRequest):
    if " " in login_request.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email không được chứa khoảng trắng",
        )

    email = login_request.email
    if "@" not in email:
        email = f"{email}@{settings.ldap_email_domain}"

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Định dạng email không hợp lệ",
        )

    expected_suffix = f"@{settings.ldap_email_domain}"
    if not email.endswith(expected_suffix):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vui lòng đăng nhập bằng tài khoản {settings.ldap_email_domain}",
        )

    try:
        with Connection(
            ldap_server,
            user=email,
            password=login_request.password,
            auto_bind=True,
        ):
            return {"detail": "Đăng nhập LDAP thành công"}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Thông tin đăng nhập không hợp lệ",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
