from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float


Base = declarative_base()

class Player(Base):
    __tablename__ = 'players'

    player_id = Column(Integer, primary_key=True)
    team = Column(String)
    height = Column(Float)
    weight = Column(String)
    wingspan = Column(Float)
    standing_reach = Column(Float)
    vertical_leap = Column(Float)
    bench_press_reps = Column(Integer)
    lane_agility_time = Column(Float)
    shuttle_run_time = Column(Float)
    # Custom Calculated Columns
    three_quarter_sprint_time_score = Column(Float)
    max_vertical_leap_score = Column(Float)
    max_bench_press_reps_score = Column(Integer)
    bmi = Column(Float)
