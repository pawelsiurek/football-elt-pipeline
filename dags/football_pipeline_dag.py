import os
import sys
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

sys.path.insert(0, "/opt/airflow/elt")

# ─────────────────────────────────────────
# Default DAG arguments
# ─────────────────────────────────────────
default_args = {
    "owner": "airflow",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
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

    return os.environ.get("COMPETITION_CODE", "PL")


# ─────────────────────────────────────────
# Task functions
# ─────────────────────────────────────────
def init_db():
    """Initialize raw tables if they don't exist"""
    from loguru import logger
    from models import create_tables
    from sqlalchemy import create_engine

    logger.info("Initializing database tables...")
    engine = create_engine(get_db_url())
    create_tables(engine)
    logger.info("Database initialization complete")


def run_matches_pipeline():
    """Extract matches from API and load into raw_matches table"""
    from extract import extract_matches
    from load import load_matches
    from loguru import logger
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    logger.info(f"Starting matches pipeline for {get_competition()}...")
    engine = create_engine(get_db_url())
    with Session(engine) as session:
        data = extract_matches(get_competition())
        load_matches(data, session)
    logger.info("Matches pipeline complete")


def run_standings_pipeline():
    """Extract standings from API and load into raw_standings table"""
    from extract import extract_standings
    from load import load_standings
    from loguru import logger
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    logger.info(f"Starting standings pipeline for {get_competition()}...")
    engine = create_engine(get_db_url())
    with Session(engine) as session:
        data = extract_standings(get_competition())
        load_standings(data, session)
    logger.info("Standings pipeline complete")


def run_scorers_pipeline():
    """Extract top scorers from API and load into raw_scorers table."""
    from extract import extract_scorers
    from load import load_scorers
    from loguru import logger
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    logger.info(f"Starting scorers pipeline for {get_competition()}...")
    engine = create_engine(get_db_url())
    with Session(engine) as session:
        data = extract_scorers(get_competition())
        load_scorers(data, session)
    logger.info("Scorers pipeline complete")


# ─────────────────────────────────────────
# DAG definition
# ─────────────────────────────────────────
with DAG(
    dag_id="football_elt_pipeline",
    default_args=default_args,
    description="Daily Premier League ELT pipeline",
    schedule_interval="0 6 * * *",  # every day at 6am
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,  # dbt swaps relations via __dbt_backup; overlapping runs collide
    tags=["football", "elt"],
) as dag:
    # Task 1 - initialize DB tables
    db_init = PythonOperator(
        task_id="db_initialization",
        python_callable=init_db,
    )

    # Tasks 2a, 2b, 2c - parallel
    sync_matches = PythonOperator(
        task_id="sync_matches",
        python_callable=run_matches_pipeline,
    )

    sync_standings = PythonOperator(
        task_id="sync_standings",
        python_callable=run_standings_pipeline,
    )

    sync_scorers = PythonOperator(
        task_id="sync_scorers",
        python_callable=run_scorers_pipeline,
    )

    # Task 3 - dbt transformations
    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/dbt_football && dbt run --profiles-dir .",
    )

    # Task 4 — dbt tests
    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="cd /opt/airflow/dbt_football && dbt test --profiles-dir .",
    )

    db_init >> [sync_matches, sync_standings, sync_scorers] >> dbt_run >> dbt_test
