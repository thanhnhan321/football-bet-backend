from .database import Base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey


class DbUser(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    name = Column(String)
    username = Column(String, unique=True)
    password = Column(String)
    department = Column(String)
    initiated_date = Column(DateTime)
    status = Column(Integer)


class DbSeason(Base):
    __tablename__ = "seasons"
    id = Column(Integer, primary_key=True, index=True)
    season_name = Column(String, unique=True)
    season_start = Column(DateTime)
    season_end = Column(DateTime)
    season_image = Column(String)
    status = Column(Integer)


class DbRole(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String, unique=True, index=True)
    description = Column(String)


class DbUserRole(Base):
    __tablename__ = "user_roles"
    idx = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    role_id = Column(Integer)


class DbMatch(Base):
    __tablename__ = "match"
    id = Column(Integer, primary_key=True, index=True)
    teamA_name = Column(String)
    teamB_name = Column(String)
    match_start = Column(DateTime)
    match_bet = Column(Integer)
    match_result = Column(String)
    season_id = Column(Integer)
    option_id = Column(Integer)
    match_description = Column(String)
    status = Column(Integer)


class DbMiniGame(Base):
    __tablename__ = "mini_game"
    id = Column(Integer, primary_key=True, index=True)
    mini_game_title = Column(String)
    mini_game_content = Column(String)
    mini_game_bet = Column(Integer)
    mini_game_start = Column(DateTime)
    mini_game_end = Column(DateTime)
    option_id = Column(Integer)
    status = Column(Integer)


class DbOption(Base):
    __tablename__ = "option"
    id = Column(Integer, primary_key=True, index=True)
    option_content = Column(String)
    match_id = Column(Integer)
    mini_game_id = Column(Integer)
    status = Column(Integer)


class DbMatchVote(Base):
    __tablename__ = "match_vote"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    match_id = Column(Integer)
    option_id = Column(Integer)
    prediction_date = Column(DateTime)
    status = Column(Integer)
