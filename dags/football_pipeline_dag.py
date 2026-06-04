from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, '/opt/airflow/elt')

# ─────────────────────────────────────────
# Default DAG arguments
# ─────────────────────────────────────────
default_args = {
    'owner': 'airflow',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
}

# ─────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────
def get_db_url() -> str:
    """Build SQLAlchemy connection string from environmental variables"""
    
    return (
        f"postgresql+psycopg2://"
        f"{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}"
        f"@{os.environ.get('DB_HOST', 'postgres')}:{os.environ.get('DB_PORT', '5432')}"
        f"/{os.environ['DB_NAME']}"
    )

def get_competition() -> str:
    """Get competition code from environment variables"""
    
    return os.environ.get('COMPETITION_CODE', 'PL')

# ─────────────────────────────────────────
# Task functions
# ─────────────────────────────────────────
def init_db():
    """Initialize raw tables if they don't exist"""
    from sqlalchemy import create_engine
    from models import create_tables
    from loguru import logger
    
    logger.info('Initializing database tables...')
    engine = create_engine(get_db_url())
    create_tables(engine)
    logger.info("Database initialization complete")

def run_matches_pipeline():
    """Extract matches from API and load into raw_matches table"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from elt.extract import extract_matches
    from elt.load import load_matches
    from loguru import logger
    
    logger.info(f'Starting matches pipeline for {get_competition()}...')
    engine = create_engine(get_db_url())
    with Session(engine) as session:
        data = extract_matches(get_competition())
        load_matches(data, session)
    logger.info('Matches pipeline complete')
 
def run_standings_pipeline():
    """Extract standings from API and load into raw_standings table"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from elt.extract import extract_standings
    from elt.load import load_standings
    from loguru import logger
    
    logger.info(f'Starting standings pipeline for {get_competition()}...')
    engine = create_engine(get_db_url())
    with Session(engine) as session:
        data = extract_standings(get_competition())
        load_standings(data, session)
    logger.info('Standings pipeline complete')   

def run_scorers_pipeline():
    """Extract top scorers from API and load into raw_scorers table."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from extract import extract_scorers
    from load import load_scorers
    from loguru import logger

    logger.info(f"Starting scorers pipeline for {get_competition()}...")
    engine = create_engine(get_db_url())
    with Session(engine) as session:
        data = extract_scorers(get_competition())
        load_scorers(data, session)
    logger.info("Scorers pipeline complete")

## LEFT IN CLAUDE + CHANGES TO PROFILES.YML
## BRANCH TO BRANCH_DAG OR SMTH
