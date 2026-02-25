from routers.schemas import UserBase, UserRole
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from database import db_user_role
from typing import List
from auth.oauth2 import get_current_user
from constant.role import ADMIN_ROLE
from database.models import DbUserRole, DbRole, DbUser


router = APIRouter(prefix="/role", tags=["role"])


@router.post(
    "/create-user-role",
    response_model=UserRole,
    dependencies=[Depends(ADMIN_ROLE)],
)
def create_user_role(
    request: UserRole,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    return db_user_role.create_user_role(db, request)


@router.get("/user-roles/{user_id}", response_model=List[str])
def get_user_roles(user_id: int, db: Session = Depends(get_db)):
    user = db.query(DbUser).filter(DbUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")

    user_roles = (
        db.query(DbRole.role_name)
        .join(DbUserRole, DbRole.id == DbUserRole.role_id)
        .filter(DbUserRole.user_id == user_id)
        .all()
    )

    if not user_roles:
        raise HTTPException(status_code=404, detail="Người dùng không có vai trò nào")

    role_names = [role[0] for role in user_roles]

    return role_names
