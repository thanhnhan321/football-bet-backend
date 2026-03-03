from sqlalchemy.orm.session import Session
from database.hash import Hash
from routers.schemas import MatchOptionBase
from database.models import DbOption, DbMatch, DbMiniGame
from fastapi import HTTPException, status
import datetime


def create_match_option(db: Session, request: MatchOptionBase):
    existing_option = (
        db.query(DbOption)
        .filter(
            DbOption.option_content.in_(request.option_content),
            DbOption.match_id == request.match_id,
        )
        .first()
    )

    if existing_option:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lựa chọn đã tồn tại",
        )

    match = db.query(DbMatch).filter(DbMatch.id == request.match_id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trận đấu không tồn tại",
        )

    for option_id in request.option_content:
        new_option = DbOption(
            option_content=option_id,
            match_id=request.match_id,
            mini_game_id=None,
            status=1,
        )

        db.add(new_option)
        db.commit()
        db.refresh(new_option)

    return HTTPException(
        status_code=status.HTTP_200_OK,
        detail="Tạo lựa chọn cho trận đấu thành công",
    )
