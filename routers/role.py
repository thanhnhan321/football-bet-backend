from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from constant.role import ADMIN_ROLE
from database import db_role
from database.database import get_db
from routers.schemas import Role, RoleBase


router = APIRouter(prefix="/role", tags=["role"])


@router.post(
    "/create-role", response_model=RoleBase, dependencies=[Depends(ADMIN_ROLE)]
)
def create_role(
    request: Role,
    db: Session = Depends(get_db),
):
    return db_role.create_role(db, request)


@router.get(
    "/role-list", response_model=List[RoleBase], dependencies=[Depends(ADMIN_ROLE)]
)
def get_all_roles(
    db: Session = Depends(get_db),
):
    return db_role.get_all_roles(db)
