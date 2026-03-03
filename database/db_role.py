from sqlalchemy.orm.session import Session
from routers.schemas import Role
from database.models import DbRole


def create_role(db: Session, request: Role):
    new_role = DbRole(
        role_name= request.role_name
    )
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role


def get_all_roles(db: Session):
    return db.query(DbRole).order_by(DbRole.id.asc()).all()
