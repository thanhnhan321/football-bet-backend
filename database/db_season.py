from sqlalchemy.orm.session import Session
from database.hash import Hash
from routers.schemas import SeasonBase, SeasonUpdateBase
from database.models import DbSeason
import datetime
from fastapi import HTTPException, status


def create_season(db: Session, request: SeasonBase):
    new_season = DbSeason(
        season_name=request.season_name,
        season_start=request.season_start,
        season_end=request.season_end,
        season_image=request.season_image,
    )

    db.add(new_season)
    db.commit()
    db.refresh(new_season)
    return HTTPException(
        status_code=status.HTTP_200_OK, detail="Tạo mùa giải thành công"
    )


def get_all_seasons(db: Session):
    seasons = db.query(DbSeason).all()
    if not seasons:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không có mùa giải nào!",
        )
    return seasons


def update_season(db: Session, id: int, request: SeasonUpdateBase):
    season = db.query(DbSeason).filter(DbSeason.id == id).first()
    if not season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mùa giải không tồn tại",
        )

    season.season_name = request.season_name
    season.season_start = request.season_start
    season.season_end = request.season_end
    season.season_image = request.season_image
    season.season_status = request.season_status

    db.commit()
    return HTTPException(
        status_code=status.HTTP_200_OK, detail="Cập nhật mùa giải thành công"
    )


def get_all_current_seasons(db: Session):
    current_date = datetime.datetime.now()
    current_seasons = (
        db.query(DbSeason)
        .filter(
            DbSeason.season_start <= current_date, DbSeason.season_end >= current_date
        )
        .all()
    )
    if not current_seasons:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hiện không có mùa giải nào đang diễn ra",
        )
    return current_seasons
