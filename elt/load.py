from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from loguru import logger
from models import RawMatch, RawStanding, RawScorer, create_tables
from config import DB_URL, COMPETITION_CODE
from extract import extract_matches, extract_standings, extract_scorers

def load_matches(data: dict, session: Session) -> None:
    """Load raw matches into raw_matches table"""
    
    matches = data["matches"]
    inserted = 0
    skipped = 0
    
    for match in matches:
        row = RawMatch(
            match_id=match["id"],
            competition=data["competition"]["name"],
            season=data["filters"]["season"],
            matchday=match["matchday"],
            status=match["status"],
            home_team=match["homeTeam"]["name"],
            away_team=match["awayTeam"]["name"],
            home_score=match["score"]["fullTime"]["home"],
            away_score=match["score"]["fullTime"]["away"],
            match_date=datetime.fromisoformat(match["utcDate"].replace("Z", "+00:00")),
            inserted_at=datetime.utcnow()
        )
        
        try:
            session.add(row)
            session.commit()
            inserted += 1
        except IntegrityError:
            session.rollback()
            skipped += 1
    
    logger.info(f"Matches - inserted: {inserted}, skipped (duplicates): {skipped}")


def load_standings(data: dict, session: Session) -> None:
    """Load raw standings into raw_standings table"""
    
    standings = data["standings"][0]["table"]
    competition = data["competition"]["name"]
    season = data["filters"]["season"]
    inserted = 0
    skipped = 0
    
    for row_data in standings:
        row = RawStanding(
            competition=competition,
            season=season,
            team=row_data["team"]["name"],
            position=row_data["position"],
            played=row_data["playedGames"],
            won=row_data["won"],
            drawn=row_data["draw"],
            lost=row_data["lost"],
            goals_for=row_data["goalsFor"],
            goals_against=row_data["goalsAgainst"],
            goal_difference=row_data["goalDifference"],
            points=row_data["points"],
            inserted_at=datetime.utcnow()
        )

        try:
            session.add(row)
            session.commit()
            inserted += 1
        except IntegrityError:
            session.rollback()
            skipped += 1
    
    logger.info(f"Standings — inserted: {inserted}, skipped (duplicates): {skipped}")


def load_scorers(data: dict, session: Session) -> None:
    """Load raw scorers into raw_scorers table"""

    scorers = data["scorers"]
    competition = data["competition"]["name"]
    season = data["filters"]["season"]
    inserted = 0
    skipped = 0

    for scorer in scorers:
        row = RawScorer(
            competition=competition,
            season=season,
            player_name=scorer["player"]["name"],
            team=scorer["team"]["name"],
            goals=scorer["goals"],
            assists=scorer.get("assists"),     
            penalties=scorer.get("penalties"),
            inserted_at=datetime.utcnow()
        )

        try:
            session.add(row)
            session.commit()
            inserted += 1
        except IntegrityError:
            session.rollback()
            skipped += 1

    logger.info(f"Scorers — inserted: {inserted}, skipped (duplicates): {skipped}")
    
if __name__ == "__main__":
    engine = create_engine(DB_URL)
    create_tables(engine)
    
    with Session(engine) as session:
        logger.info("Starting load...")
        
        matches_data = extract_matches(COMPETITION_CODE)
        load_matches(matches_data, session=session)
        
        standings_data = extract_standings(COMPETITION_CODE)
        load_standings(standings_data, session=session)
        
        scorers_data = extract_scorers(COMPETITION_CODE)
        load_scorers(scorers_data, session)

        logger.info("Load complete!")
        
        