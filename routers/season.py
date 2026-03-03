from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from database import db_season
from typing import List
from auth.oauth2 import get_current_user
from routers.schemas import SeasonBase, SeasonDisplay, UserBase, SeasonUpdateBase
from constant.role import ADMIN_ROLE, ALL_ROLE

router = APIRouter(prefix="/season", tags=["season"])


@router.post(
    "/create-season",
    dependencies=[Depends(ADMIN_ROLE)],
)
async def create_season(
    request: SeasonBase,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    return db_season.create_season(db, request)


@router.get(
    "/season-list",
    response_model=List[SeasonDisplay],
    dependencies=[Depends(ALL_ROLE)],
)
def get_all_seasons(
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    return db_season.get_all_seasons(db)


@router.post(
    "/update-season/{id}",
    dependencies=[Depends(ADMIN_ROLE)],
)
def update_season(
    id: int,
    request: SeasonUpdateBase,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    return db_season.update_season(db, id, request)


@router.get(
    "/current-seasons",
    response_model=List[SeasonDisplay],
    dependencies=[Depends(ALL_ROLE)],
)
def get_all_current_seasons(
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    return db_season.get_all_current_seasons(db)
