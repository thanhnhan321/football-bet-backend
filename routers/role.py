from routers.schemas import RoleBase, Role
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from database import db_role
from routers.schemas import UserBase
from auth.oauth2 import get_current_user
from constant.role import ADMIN_ROLE


router = APIRouter(prefix="/role", tags=["role"])


@router.post(
    "/create-role", response_model=RoleBase, dependencies=[Depends(ADMIN_ROLE)]
)
def create_role(
    request: Role,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    return db_role.create_role(db, request)
