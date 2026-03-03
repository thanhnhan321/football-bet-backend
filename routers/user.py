from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from constant.role import ADMIN_ROLE
from database import db_user
from database.database import get_db
from routers.schemas import UserBase, UserDisplay, UserUpdateBase

router = APIRouter(prefix="/user", tags=["user"])


@router.post(
    "/create-user",
    dependencies=[Depends(ADMIN_ROLE)],
)
def create_user(
    request: UserBase,
    db: Session = Depends(get_db),
):
    return db_user.create_user(db, request)


@router.get(
    "/user-list",
    response_model=List[UserDisplay],
    dependencies=[Depends(ADMIN_ROLE)],
)
def get_all_users(
    db: Session = Depends(get_db),
):
    return db_user.get_all_users(db)


@router.put(
    "/update-user/{id}",
    dependencies=[Depends(ADMIN_ROLE)],
)
def update_user(
    id: int,
    request: UserUpdateBase,
    db: Session = Depends(get_db),
):
    return db_user.update_user(db, id, request)


@router.put(
    "/delete-user/{id}",
    dependencies=[Depends(ADMIN_ROLE)],
)
def delete_user(
    id: int,
    db: Session = Depends(get_db),
):
    return db_user.delete_user(db, id)
