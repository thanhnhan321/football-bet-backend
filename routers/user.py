from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from database import db_user
from typing import List
from auth.oauth2 import get_current_user
from routers.schemas import UserBase, UserDisplay, UserUpdateBase
from constant.role import ADMIN_ROLE

router = APIRouter(prefix="/user", tags=["user"])


@router.post(
    "/create-user",
    dependencies=[Depends(ADMIN_ROLE)],
)
async def create_user(
    request: UserBase,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    return db_user.create_user(db, request)


@router.get(
    "/user-list",
    response_model=List[UserBase],
    dependencies=[Depends(ADMIN_ROLE)],
)
def get_all_users(
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    return db_user.get_all_users(db)


@router.post(
    "/update-user/{id}",
    dependencies=[Depends(ADMIN_ROLE)],
)
def update_user(
    id: int,
    request: UserUpdateBase,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    return db_user.update_user(db, id, request)
