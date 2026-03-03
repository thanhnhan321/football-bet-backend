from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from database import db_mini_game
from auth.oauth2 import get_current_user
from routers.schemas import MiniGameBase, UserBase
from constant.role import ADMIN_ROLE

router = APIRouter(prefix="/mini-game", tags=["mini_game"])


@router.post("/create-mini-game", dependencies=[Depends(ADMIN_ROLE)])
async def create_mini_game(
    request: MiniGameBase,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    return db_mini_game.create_mini_game(db, request)
