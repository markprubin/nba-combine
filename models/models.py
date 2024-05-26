from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float


Base = declarative_base()

class Player(Base):

    __tablename__ = 'players'

    player_id = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    position = Column(String)
    team = Column(String)
    season_year = Column(String, primary_key=True, nullable=False)
    height = Column(Float)
    weight = Column(String)
    wingspan = Column(Float)
    standing_reach = Column(Float)
    standing_vertical_leap = Column(Float)
    lane_agility_time = Column(Float)
    shuttle_run_time = Column(Float)
    three_quarter_sprint_time = Column(Float)
    three_quarter_sprint_time_score = Column(Float)
    max_vertical_leap = Column(Float)
    max_vertical_leap_score = Column(Float)
    max_bench_press_reps = Column(Integer)
    max_bench_press_reps_score = Column(Float)
    bmi = Column(Float)
