"""Shared pytest fixtures: fake API payloads and a throwaway SQLite session.

The payloads mirror the shape of football-data.org v4 responses (only the fields
the loaders actually read), so tests exercise the real key paths the code walks.
"""

import models
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


@pytest.fixture
def matches_payload() -> dict:
    """Two matches: one FINISHED (has scores), one SCHEDULED (scores are null)."""
    return {
        "competition": {"name": "Premier League"},
        "filters": {"season": "2024"},
        "matches": [
            {
                "id": 1001,
                "matchday": 1,
                "status": "FINISHED",
                "homeTeam": {"name": "Arsenal FC"},
                "awayTeam": {"name": "Chelsea FC"},
                "score": {"fullTime": {"home": 2, "away": 1}},
                "utcDate": "2024-08-17T14:00:00Z",
            },
            {
                "id": 1002,
                "matchday": 1,
                "status": "SCHEDULED",
                "homeTeam": {"name": "Liverpool FC"},
                "awayTeam": {"name": "Everton FC"},
                "score": {"fullTime": {"home": None, "away": None}},
                "utcDate": "2024-08-18T14:00:00Z",
            },
        ],
    }


@pytest.fixture
def standings_payload() -> dict:
    """League table with two teams. season is an int to exercise str() coercion."""
    return {
        "competition": {"name": "Premier League"},
        "filters": {"season": 2024},
        "standings": [
            {
                "table": [
                    {
                        "team": {"name": "Arsenal FC"},
                        "position": 1,
                        "playedGames": 10,
                        "won": 8,
                        "draw": 1,
                        "lost": 1,
                        "goalsFor": 20,
                        "goalsAgainst": 8,
                        "goalDifference": 12,
                        "points": 25,
                    },
                    {
                        "team": {"name": "Chelsea FC"},
                        "position": 2,
                        "playedGames": 10,
                        "won": 7,
                        "draw": 2,
                        "lost": 1,
                        "goalsFor": 18,
                        "goalsAgainst": 9,
                        "goalDifference": 9,
                        "points": 23,
                    },
                ]
            }
        ],
    }


@pytest.fixture
def scorers_payload() -> dict:
    """Two scorers: one full row, one missing the optional assists/penalties keys."""
    return {
        "competition": {"name": "Premier League"},
        "filters": {"season": 2024},
        "scorers": [
            {
                "player": {"name": "Bukayo Saka"},
                "team": {"name": "Arsenal FC"},
                "goals": 10,
                "assists": 5,
                "penalties": 2,
            },
            {
                # No "assists"/"penalties" keys -> loader must fall back to None.
                "player": {"name": "Cole Palmer"},
                "team": {"name": "Chelsea FC"},
                "goals": 9,
            },
        ],
    }


@pytest.fixture
def sqlite_session():
    """An isolated in-memory SQLite DB with the raw_* tables created.

    load_matches() is plain ORM (add/commit), so it runs faithfully on SQLite —
    including the UNIQUE(match_id) constraint that drives duplicate-skipping.
    """
    engine = create_engine("sqlite:///:memory:")
    models.create_tables(engine)
    with Session(engine) as session:
        yield session
