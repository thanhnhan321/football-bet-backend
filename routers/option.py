from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from database import db_option
from typing import List
from auth.oauth2 import get_current_user
from routers.schemas import UserBase, MatchOptionBase
from constant.role import ADMIN_ROLE

router = APIRouter(prefix="/option", tags=["option"])


@router.post(
    "/create-option",
    dependencies=[Depends(ADMIN_ROLE)],
)
async def create_match_option(
    request: MatchOptionBase,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    return db_option.create_match_option(db, request)
