import datetime
import re

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session

from database.hash import Hash
from database.models import DbUser
from routers.schemas import UserBase, UserUpdateBase


def create_user(db: Session, request: UserBase):
    if " " in request.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email không được chứa khoảng trắng",
        )

    if not re.match(r"[^@]+@[^@]+\.[^@]+", request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Định dạng email không hợp lệ",
        )

    existing_user = db.query(DbUser).filter(DbUser.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Địa chỉ email đã tồn tại",
        )

    if " " in request.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username không được chứa khoảng trắng",
        )

    existing_username = (
        db.query(DbUser).filter(DbUser.username == request.username).first()
    )
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username đã tồn tại",
        )

    if " " in request.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password không được chứa khoảng trắng",
        )

    new_user = DbUser(
        email=request.email,
        name=request.name,
        username=request.username,
        password=Hash.bcrypt(request.password),
        department=request.department,
        initiated_date=datetime.datetime.now(),
        status=1,
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email hoặc username đã tồn tại",
        ) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể tạo người dùng",
        ) from exc

    return {"detail": "Tạo người dùng thành công", "id": new_user.id}


def get_user_by_username(db: Session, username: str):
    return db.query(DbUser).filter(DbUser.username == username).first()


def get_all_users(db: Session):
    return db.query(DbUser).all()


def update_user(db: Session, id: int, request: UserUpdateBase):
    user = db.query(DbUser).filter(DbUser.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User không tồn tại",
        )

    if " " in request.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email không được chứa khoảng trắng",
        )

    if not re.match(r"[^@]+@[^@]+\.[^@]+", request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Định dạng email không hợp lệ",
        )

    existing_email = db.query(DbUser).filter(DbUser.email == request.email).first()
    if existing_email and existing_email.id != id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Địa chỉ email đã tồn tại",
        )

    if " " in request.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username không được chứa khoảng trắng",
        )

    existing_username = (
        db.query(DbUser).filter(DbUser.username == request.username).first()
    )
    if existing_username and existing_username.id != id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username đã tồn tại",
        )

    if " " in request.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password không được chứa khoảng trắng",
        )

    user.email = request.email
    user.name = request.name
    user.username = request.username
    user.password = Hash.bcrypt(request.password)
    user.department = request.department
    user.initiated_date = request.initiated_date
    user.status = request.status

    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể cập nhật người dùng",
        ) from exc

    return {"detail": "Cập nhật người dùng thành công"}
