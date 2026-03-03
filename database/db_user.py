import datetime
import re

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session

from database.hash import Hash
from database.models import DbDepartment, DbRole, DbUser, DbUserRole
from routers.schemas import UserBase, UserUpdateBase

DEFAULT_MEMBER_ROLE_NAME = "member"


def _get_valid_department_name(db: Session, department_name: str) -> str:
    normalized = department_name.strip()
    if not normalized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bộ phận không được để trống",
        )

    department = (
        db.query(DbDepartment)
        .filter(DbDepartment.department_name == normalized)
        .first()
    )
    if not department:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bộ phận không tồn tại",
        )

    return department.department_name


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
    department_name = _get_valid_department_name(db, request.department)
    initial_password = request.username.strip()
    if not initial_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username không được để trống",
        )

    new_user = DbUser(
        email=request.email,
        name=request.name,
        username=request.username,
        password=Hash.bcrypt(initial_password),
        department=department_name,
        initiated_date=datetime.datetime.now(),
    )

    try:
        db.add(new_user)
        db.flush()

        member_role = (
            db.query(DbRole)
            .filter(DbRole.role_name == DEFAULT_MEMBER_ROLE_NAME)
            .first()
        )
        if not member_role:
            member_role = DbRole(role_name=DEFAULT_MEMBER_ROLE_NAME)
            db.add(member_role)
            db.flush()

        db.add(DbUserRole(user_id=new_user.id, role_id=member_role.id))
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
    users = db.query(DbUser).order_by(DbUser.id.asc()).all()
    if not users:
        return []

    user_ids = [user.id for user in users]
    role_rows = (
        db.query(DbUserRole.user_id, DbRole.role_name)
        .join(DbRole, DbRole.id == DbUserRole.role_id)
        .filter(DbUserRole.user_id.in_(user_ids))
        .all()
    )

    roles_by_user = {}
    for user_id, role_name in role_rows:
        roles_by_user.setdefault(user_id, []).append(role_name)

    return [
        {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "username": user.username,
            "department": user.department,
            "initiated_date": user.initiated_date,
            "roles": roles_by_user.get(user.id, []),
        }
        for user in users
    ]


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

    department_name = _get_valid_department_name(db, request.department)

    password_text = (request.password or "").strip()
    if password_text and " " in password_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password không được chứa khoảng trắng",
        )

    user.email = request.email
    user.name = request.name
    user.username = request.username
    if password_text:
        user.password = Hash.bcrypt(password_text)
    user.department = department_name

    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể cập nhật người dùng",
        ) from exc

    return {"detail": "Cập nhật người dùng thành công"}


def delete_user(db: Session, id: int):
    user = db.query(DbUser).filter(DbUser.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User không tồn tại",
        )

    try:
        db.query(DbUserRole).filter(DbUserRole.user_id == id).delete(
            synchronize_session=False
        )
        db.delete(user)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể xóa người dùng",
        ) from exc

    return {"detail": "Xóa người dùng thành công"}
