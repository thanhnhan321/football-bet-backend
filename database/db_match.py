from sqlalchemy.orm.session import Session
from database.hash import Hash
from routers.schemas import MatchBase, MatchUpdateBase
from database.models import DbMatch, DbSeason
from fastapi import HTTPException, status, Response
import datetime


def create_match(db: Session, request: MatchBase):
    season = db.query(DbSeason).filter(DbSeason.id == request.season_id).first()
    if not season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mùa giải không tồn tại"
        )
    new_match = DbMatch(
        teamA_name=request.teamA_name,
        teamB_name=request.teamB_name,
        match_start=datetime.datetime.now(),
        match_bet=request.match_bet,
        match_result=None,
        season_id=request.season_id,
        option_id=None,
        AgivesB=request.AgivesB,
        status=1,
    )

    db.add(new_match)
    db.commit()
    db.refresh(new_match)
    return HTTPException(status_code=status.HTTP_200_OK, detail="Tạo trận thành công")


def get_match(db: Session, id: int):
    match = db.query(DbMatch).filter(DbMatch.id == id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trận đấu với id là {id} không tìm thấy",
        )
    return match


def update_match(db: Session, id: int, request: MatchUpdateBase):
    match = db.query(DbMatch).filter(DbMatch.id == id)
    if not match.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trận không tồn tại",
        )
    match.update(
        {
            DbMatch.teamA_name: request.teamA_name,
            DbMatch.teamB_name: request.teamB_name,
            DbMatch.match_start: request.match_start,
            DbMatch.match_bet: request.match_bet,
            DbMatch.match_result: request.match_result,
            DbMatch.season_id: request.season_id,
            DbMatch.option_id: request.option_id,
            DbMatch.AgivesB: request.AgivesB,
            DbMatch.status: request.status,
        }
    )
    db.commit()
    return HTTPException(
        status_code=status.HTTP_200_OK, detail="Cập nhật trận thành công"
    )


def delete_match(db: Session, match_id: int):
    match = db.query(DbMatch).filter(DbMatch.id == match_id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trận đấu không tồn tại",
        )

    match.status = 0
    db.commit()
    return HTTPException(status_code=status.HTTP_200_OK, detail="Xóa trận thành công")
