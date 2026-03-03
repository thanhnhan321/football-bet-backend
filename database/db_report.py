from database.models import DbUser, DbMatch, DbMatchVote, DbOption, DbSeason
from openpyxl import Workbook
from typing import List
from sqlalchemy.orm import Session


def generate_match_vote_excel_data(votes: List[DbMatchVote], db: Session):
    wb = Workbook()
    ws = wb.active

    ws.append(
        [
            "Mùa giải",
            "Bóng lăn lúc",
            "Đội A",
            "Đội B",
            "A chấp B",
            "Tỉ số",
            "Người chơi",
            "Lựa chọn",
            "Chọn lúc",
            "Kết quả",
            "Số tiền",
        ]
    )

    for vote in votes:
        match = db.query(DbMatch).filter(DbMatch.id == vote.match_id).first()
        if match:
            option = db.query(DbOption).filter(DbOption.id == vote.option_id).first()
            if option:
                if option.id == match.option_id:
                    result = "Thắng"
                    cost = 0
                else:
                    result = "Thua"
                    cost = -match.match_bet
        user = db.query(DbUser).filter(DbUser.id == vote.user_id).first()
        match_option = (
            db.query(DbOption).filter(DbOption.match_id == vote.match_id).first()
        )
        season_name = None
        if match.season_id:
            season = db.query(DbSeason).filter(DbSeason.id == match.season_id).first()
            if season:
                season_name = season.season_name
        if match and user and match_option:
            ws.append(
                [
                    season_name,
                    match.match_start,
                    match.teamA_name,
                    match.teamB_name,
                    match.AgivesB,
                    match.match_result,
                    user.name,
                    option.option_content,
                    vote.prediction_date,
                    result,
                    cost,
                ]
            )

    wb.save("match_votes.xlsx")
