from datetime import datetime
from typing import List

from pydantic import BaseModel


class MiniGameBase(BaseModel):
    mini_game_title: str
    mini_game_content: str
    mini_game_bet: int
    mini_game_start: datetime
    mini_game_end: datetime


class MatchBase(BaseModel):
    teamA_name: str
    teamB_name: str
    match_start: datetime
    match_bet: int
    season_id: int
    AgivesB: int


class MatchUpdateBase(BaseModel):
    teamA_name: str
    teamB_name: str
    match_start: datetime
    match_bet: int
    match_result: str
    season_id: int
    option_id: int
    AgivesB: int
    status: int


class UserBase(BaseModel):
    email: str
    name: str
    username: str
    password: str
    department: str


class SeasonBase(BaseModel):
    season_name: str
    season_start: datetime
    season_end: datetime
    season_image: str


class UserDisplay(BaseModel):
    id: int
    email: str
    name: str
    username: str
    department: str
    initiated_date: datetime
    status: int

    class Config:
        from_attributes = True


class User(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    id: int
    role_name: str


class Role(BaseModel):
    role_name: str


class UserRole(BaseModel):
    user_id: int
    role_id: int


class RefreshToken(BaseModel):
    refresh_token: str


class MatchOptionBase(BaseModel):
    option_content: List[str]
    match_id: int


class LoginRequest(BaseModel):
    email: str
    password: str


class UserUpdateBase(BaseModel):
    email: str
    name: str
    username: str
    password: str
    department: str
    initiated_date: datetime
    status: int


class SeasonUpdateBase(BaseModel):
    season_name: str
    season_start: datetime
    season_end: datetime
    season_image: str
    season_status: int
