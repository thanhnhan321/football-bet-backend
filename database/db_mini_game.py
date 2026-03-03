from sqlalchemy.orm.session import Session
from database.hash import Hash
from routers.schemas import MiniGameBase
from database.models import DbMiniGame
from fastapi import HTTPException, status
import datetime


def create_mini_game(db: Session, request: MiniGameBase):
    new_mini_game = DbMiniGame(
        mini_game_title=request.mini_game_title,
        mini_game_content=request.mini_game_content,
        mini_game_bet=request.mini_game_bet,
        mini_game_start=request.mini_game_start,
        mini_game_end=request.mini_game_end,
        option_id=None,
        status=1,
    )

    db.add(new_mini_game)
    db.commit()
    db.refresh(new_mini_game)
    return HTTPException(
        status_code=status.HTTP_200_OK, detail="Tạo mini game thành công"
    )
