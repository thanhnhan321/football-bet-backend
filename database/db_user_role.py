from sqlalchemy.orm.session import Session
from fastapi import HTTPException, status

from routers.schemas import UserRole
from database.models import DbRole, DbUser, DbUserRole


def create_user_role(db: Session, request: UserRole):
    user = db.query(DbUser).filter(DbUser.id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng không tồn tại",
        )

    role = db.query(DbRole).filter(DbRole.id == request.role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vai trò không tồn tại",
        )

    existing = (
        db.query(DbUserRole)
        .filter(
            DbUserRole.user_id == request.user_id,
            DbUserRole.role_id == request.role_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Người dùng đã có vai trò này",
        )

    new_user_role = DbUserRole(user_id=request.user_id, role_id=request.role_id)
    db.add(new_user_role)
    db.commit()
    db.refresh(new_user_role)
    return new_user_role
