from sqlalchemy.orm.session import Session
from database.hash import Hash
from routers.schemas import MatchBase, MatchUpdateBase
from database.models import DbMatch, DbSeason
from fastapi import HTTPException, status, Response
import datetime
import math


def _is_half_step(value: float) -> bool:
    return math.isclose(value * 2, round(value * 2), rel_tol=0, abs_tol=1e-9)


def _is_future_datetime(value: datetime.datetime) -> bool:
    local_tz = datetime.datetime.now().astimezone().tzinfo
    now = datetime.datetime.now(local_tz)
    candidate = value.replace(tzinfo=local_tz) if value.tzinfo is None else value.astimezone(local_tz)
    return candidate > now


def create_match(db: Session, request: MatchBase):
    season = db.query(DbSeason).filter(DbSeason.id == request.season_id).first()
    if not season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mùa giải không tồn tại"
        )
    if not _is_future_datetime(request.match_start):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Giờ bóng lăn phải là thời gian ở tương lai",
        )
    if not _is_half_step(request.AgivesB):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A chấp B phải là số nguyên hoặc dạng .5",
        )
    new_match = DbMatch(
        teamA_name=request.teamA_name,
        teamB_name=request.teamB_name,
        match_start=request.match_start,
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


def get_all_matches(db: Session):
    return (
        db.query(DbMatch)
        .filter(DbMatch.status == 1)
        .order_by(DbMatch.id.desc())
        .all()
    )


def update_match(db: Session, id: int, request: MatchUpdateBase):
    match = db.query(DbMatch).filter(DbMatch.id == id)
    if not match.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trận không tồn tại",
        )
    if not _is_half_step(request.AgivesB):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A chấp B phải là số nguyên hoặc dạng .5",
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
