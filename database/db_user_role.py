from sqlalchemy.orm.session import Session
from routers.schemas import UserRole
from database.models import DbUserRole


def create_user_role(db: Session, request: UserRole):
    new_user_role = DbUserRole(user_id=request.user_id, role_id=request.role_id)
    db.add(new_user_role)
    db.commit()
    db.refresh(new_user_role)
    return new_user_role
