from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from database import db_match
from typing import List
from auth.oauth2 import get_current_user
from routers.schemas import MatchBase, UserBase, MatchUpdateBase
from constant.role import ADMIN_ROLE, ALL_ROLE
from database.db_match import delete_match

router = APIRouter(prefix="/match", tags=["match"])


@router.get(
    "/match-list",
    dependencies=[Depends(ALL_ROLE)],
)
def get_match_list(
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    return db_match.get_all_matches(db)


@router.post(
    "/create-match",
    dependencies=[Depends(ADMIN_ROLE)],
)
async def create_match(
    request: MatchBase,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    return db_match.create_match(db, request)


@router.get(
    "/get-match/{id}",
    response_model=MatchBase,
    dependencies=[Depends(ALL_ROLE)],
)
def get_match(
    id: int,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    return db_match.get_match(db, id)


@router.post(
    "/update-match/{id}",
    dependencies=[Depends(ADMIN_ROLE)],
)
def update_match(
    id: int,
    request: MatchUpdateBase,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    return db_match.update_match(db, id, request)


@router.put(
    "/delete-match/{match_id}",
    dependencies=[Depends(ADMIN_ROLE)],
)
def delete_match_endpoint(
    match_id: int,
    db: Session = Depends(get_db),
):
    return delete_match(db, match_id)
