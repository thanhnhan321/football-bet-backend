from datetime import datetime
from typing import List, Optional

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
    AgivesB: float


class MatchUpdateBase(BaseModel):
    teamA_name: str
    teamB_name: str
    match_start: datetime
    match_bet: int
    match_result: str
    season_id: int
    option_id: int
    AgivesB: float
    status: int


class UserBase(BaseModel):
    email: str
    name: str
    username: str
    department: str


class DepartmentBase(BaseModel):
    department_name: str


class DepartmentDisplay(DepartmentBase):
    id: int

    class Config:
        from_attributes = True


class SeasonBase(BaseModel):
    season_name: str
    season_start: datetime
    season_end: datetime
    season_image: str


class SeasonDisplay(SeasonBase):
    id: int

    class Config:
        from_attributes = True


class UserDisplay(BaseModel):
    id: int
    email: str
    name: str
    username: str
    department: str
    initiated_date: datetime
    roles: List[str] = []

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


class FirstLoginPasswordChangeRequest(BaseModel):
    username: str
    current_password: str
    new_password: str


class MatchOptionBase(BaseModel):
    option_content: List[str]
    match_id: int


class UserUpdateBase(BaseModel):
    email: str
    name: str
    username: str
    department: str
    password: Optional[str] = None


class SeasonUpdateBase(BaseModel):
    season_name: str
    season_start: datetime
    season_end: datetime
    season_image: str
