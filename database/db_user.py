from sqlalchemy.orm.session import Session
from database.hash import Hash
from routers.schemas import UserBase, UserUpdateBase
from database.models import DbUser, DbUserRole
from fastapi import HTTPException, status
import datetime
import re


def create_user(db: Session, request: UserBase):
    if " " in request.email:
        raise HTTPException(
            status_code=400, detail="Email không được chứa khoảng trắng"
        )

    if not re.match(r"[^@]+@[^@]+\.[^@]+", request.email):
        raise HTTPException(status_code=400, detail="Định dạng email không hợp lệ")

    existing_user = db.query(DbUser).filter(DbUser.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Địa chỉ email đã tồn tại")

    if " " in request.username:
        raise HTTPException(
            status_code=400, detail="Username không được chứa khoảng trắng"
        )

    existing_username = (
        db.query(DbUser).filter(DbUser.username == request.username).first()
    )
    if existing_username:
        raise HTTPException(status_code=400, detail="Username đã tồn tại")

    if " " in request.password:
        raise HTTPException(
            status_code=400, detail="Password không được chứa khoảng trắng"
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

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    new_user_role = DbUserRole(user_id=new_user.id, role_id=2)
    db.add(new_user_role)
    db.commit()
    return HTTPException(
        status_code=status.HTTP_200_OK, detail="Tạo người dùng thành công"
    )


def get_user_by_username(db: Session, username: str):
    user = db.query(DbUser).filter(DbUser.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User username {username} not found",
        )
    return user


def get_all_users(db: Session):
    users = db.query(DbUser).all()
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không có mùa người chơi nào!",
        )
    return users


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
            status_code=status.HTTP_400_BAD_REQUEST, detail="Địa chỉ email đã tồn tại"
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
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username đã tồn tại"
        )

    if " " in request.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password không được chứa khoảng trắng",
        )

    user.email = request.email
    user.name = request.name
    user.username = request.username
    user.password = request.password
    user.department = request.department
    user.initiated_date = request.initiated_date
    user.status = request.status

    db.commit()
    return HTTPException(
        status_code=status.HTTP_200_OK, detail="Cập nhật mùa giải thành công"
    )
