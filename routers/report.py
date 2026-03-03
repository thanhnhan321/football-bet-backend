from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import DbMatchVote
from database.db_report import generate_match_vote_excel_data
from starlette.responses import StreamingResponse

router = APIRouter(prefix="/report", tags=["report"])


@router.get("/export-match-votes-excel")
async def export_match_votes_excel(response: Response, db: Session = Depends(get_db)):
    votes = db.query(DbMatchVote).all()

    generate_match_vote_excel_data(votes, db)

    with open("match_votes.xlsx", "rb") as excel_file:
        content = excel_file.read()

    return StreamingResponse(
        content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
