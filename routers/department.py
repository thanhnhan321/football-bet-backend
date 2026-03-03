from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from constant.role import ADMIN_ROLE
from database import db_department
from database.database import get_db
from routers.schemas import DepartmentBase, DepartmentDisplay

router = APIRouter(prefix="/department", tags=["department"])


@router.post(
    "/create-department",
    response_model=DepartmentDisplay,
    dependencies=[Depends(ADMIN_ROLE)],
)
def create_department(
    request: DepartmentBase,
    db: Session = Depends(get_db),
):
    return db_department.create_department(db, request)


@router.get(
    "/department-list",
    response_model=List[DepartmentDisplay],
    dependencies=[Depends(ADMIN_ROLE)],
)
def get_department_list(
    db: Session = Depends(get_db),
):
    return db_department.get_all_departments(db)
