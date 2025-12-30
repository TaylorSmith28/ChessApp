from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Opening(Base):
    __tablename__ = 'openings'
    id = Column(Integer, primary_key=True)

class Game(Base):
    __tablename__ = 'games'
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True)
    white_username = Column(String, nullable=False)
    black_username = Column(String, nullable=False)
    white_rating = Column(Integer)
    black_rating = Column(Integer)
    time_control = Column(String)
    end_time = Column(DateTime)
    pgn = Column(Text)
    result = Column(String)
    opening_id = Column(String)
    elo_change_white = Column(Float)
    elo_change_black = Column(Float)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User")

# SQLite Engine
engine = create_engine('sqlite:///chess_analytics.db', echo=False)

# Create tables
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)