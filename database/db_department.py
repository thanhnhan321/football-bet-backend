from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session

from database.models import DbDepartment
from routers.schemas import DepartmentBase


def create_department(db: Session, request: DepartmentBase):
    department_name = request.department_name.strip()
    if not department_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tên bộ phận không được để trống",
        )

    existing = (
        db.query(DbDepartment)
        .filter(DbDepartment.department_name.ilike(department_name))
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bộ phận đã tồn tại",
        )

    new_department = DbDepartment(department_name=department_name)
    try:
        db.add(new_department)
        db.commit()
        db.refresh(new_department)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bộ phận đã tồn tại",
        ) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể tạo bộ phận",
        ) from exc

    return new_department


def get_all_departments(db: Session):
    return db.query(DbDepartment).order_by(DbDepartment.id.asc()).all()
