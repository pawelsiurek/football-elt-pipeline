"""Fixtures for Postgres-backed integration tests.

These only run when TEST_DATABASE_URL points at a disposable Postgres (CI sets
it to the service-container DB). Absent that env var, every test here skips, so a
plain local `pytest` never touches a real database.
"""

import os

import models
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

RAW_TABLES = ("raw_matches", "raw_standings", "raw_scorers")


@pytest.fixture
def pg_session():
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL not set; skipping Postgres integration tests")

    engine = create_engine(url)
    models.create_tables(engine)
    # Start each test from empty raw_* tables so results are deterministic.
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE {', '.join(RAW_TABLES)} RESTART IDENTITY CASCADE"))

    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
        engine.dispose()
