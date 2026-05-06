from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import declarative_base
from config import DB_URL

Base = declarative_base()

class RawMatch(Base):
    __tablename__ = "raw_matches"
    
    id          = Column(Integer, primary_key=True)
    match_id    = Column(Integer, unique=True, nullable=False)
    competition = Column(String)
    season      = Column(String)
    matchday    = Column(Integer)
    status      = Column(String)
    home_team   = Column(String)
    away_team   = Column(String)
    home_score  = Column(Integer)
    away_score  = Column(Integer)
    match_date  = Column(DateTime)
    inserted_at = Column(DateTime)

class RawStanding(Base):
    __tablename__ = "raw_standings"
    
    id              = Column(Integer, primary_key=True)
    competition     = Column(String)
    season          = Column(String)
    team            = Column(String, unique=True, nullable=False)
    position        = Column(Integer)
    played          = Column(Integer)
    won             = Column(Integer)
    drawn           = Column(Integer)
    lost            = Column(Integer)
    goals_for       = Column(Integer)
    goals_against   = Column(Integer)
    goal_difference = Column(Integer)
    points          = Column(Integer)
    inserted_at     = Column(DateTime)

class RawScorer(Base):
    __tablename__ = "raw_scorers"
    
    id          = Column(Integer, primary_key=True)
    competition = Column(String)
    season      = Column(String)
    player_name = Column(String, nullable=False)
    team        = Column(String)
    goals       = Column(Integer)
    assists     = Column(Integer)
    penalties   = Column(Integer)
    inserted_at = Column(DateTime)

def create_tables(engine):
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    engine = create_engine(DB_URL)
    create_tables(engine)
    print("Tables created successfully")