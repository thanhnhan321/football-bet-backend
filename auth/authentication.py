from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth import oauth2
from database import models
from database.database import get_db
from database.hash import Hash
from routers.schemas import FirstLoginPasswordChangeRequest, RefreshToken

router = APIRouter(tags=["authentication"])
FIRST_LOGIN_REQUIRED_DETAIL = (
    "Tài khoản đang dùng mật khẩu mặc định. Vui lòng đổi mật khẩu trước khi đăng nhập."
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
    if Hash.verify(user.password, user.username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=FIRST_LOGIN_REQUIRED_DETAIL,
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
        "name": user.name,
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


@router.post("/first-login/change-password")
def change_password_first_login(
    request: FirstLoginPasswordChangeRequest,
    db: Session = Depends(get_db),
):
    username = request.username.strip()
    current_password = request.current_password.strip()
    new_password = request.new_password.strip()

    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username không được để trống",
        )
    if not current_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu hiện tại không được để trống",
        )
    if not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu mới không được để trống",
        )
    if " " in new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu mới không được chứa khoảng trắng",
        )
    if new_password == username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu mới không được trùng username",
        )

    user = db.query(models.DbUser).filter(models.DbUser.username == username).first()
    if not user or not Hash.verify(user.password, current_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Thông tin đăng nhập không hợp lệ",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not Hash.verify(user.password, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản đã đổi mật khẩu, vui lòng đăng nhập",
        )

    user.password = Hash.bcrypt(new_password)
    db.commit()

    return {"detail": "Đổi mật khẩu lần đầu thành công"}
