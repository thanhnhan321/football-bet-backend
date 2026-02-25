from fastapi import FastAPI
from database import models
from database.database import engine
from routers import user, role, user_role
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from auth import authentication


app = FastAPI()
app.include_router(authentication.router)
app.include_router(role.router)
app.include_router(user.router)
app.include_router(user_role.router)
models.Base.metadata.create_all(bind=engine)

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
