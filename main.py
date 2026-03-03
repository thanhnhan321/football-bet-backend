from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth import authentication
from core.config import settings
from database import models
from database.database import engine
from routers import role, user, user_role, season, match, mini_game, option, report

app = FastAPI()


@app.on_event("startup")
def on_startup() -> None:
    if settings.auto_create_tables:
        models.Base.metadata.create_all(bind=engine)


app.include_router(authentication.router)
app.include_router(role.router)
app.include_router(user.router)
app.include_router(user_role.router)
app.include_router(season.router)
app.include_router(match.router)
app.include_router(mini_game.router)
app.include_router(option.router)
app.include_router(report.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
