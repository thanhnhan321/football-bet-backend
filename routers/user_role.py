from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from constant.role import ADMIN_ROLE
from database import db_user_role
from database.database import get_db
from database.models import DbRole, DbUser, DbUserRole
from routers.schemas import UserRole

router = APIRouter(prefix="/role", tags=["role"])


@router.post(
    "/create-user-role",
    response_model=UserRole,
    dependencies=[Depends(ADMIN_ROLE)],
)
def create_user_role(
    request: UserRole,
    db: Session = Depends(get_db),
):
    return db_user_role.create_user_role(db, request)


@router.get(
    "/user-roles/{user_id}",
    response_model=List[str],
    dependencies=[Depends(ADMIN_ROLE)],
)
def get_user_roles(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = db.query(DbUser).filter(DbUser.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng không tồn tại",
        )

    user_roles = (
        db.query(DbRole.role_name)
        .join(DbUserRole, DbRole.id == DbUserRole.role_id)
        .filter(DbUserRole.user_id == user_id)
        .all()
    )

    if not user_roles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng không có vai trò nào",
        )

    return [role[0] for role in user_roles]
