from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint, create_engine
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

    # A standings row is one team's line in one season's table, so the natural
    # grain is (competition, season, team) — NOT team alone. Keying on team
    # alone froze each team at its first-seen season and blocked later seasons.
    __table_args__ = (
        UniqueConstraint("competition", "season", "team",
                         name="uq_standings_comp_season_team"),
    )

    id              = Column(Integer, primary_key=True)
    competition     = Column(String)
    season          = Column(String)
    team            = Column(String, nullable=False)
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

    # One row per player per season; without this the loader appended a fresh
    # copy of every scorer on each run.
    __table_args__ = (
        UniqueConstraint("competition", "season", "player_name",
                         name="uq_scorers_comp_season_player"),
    )

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