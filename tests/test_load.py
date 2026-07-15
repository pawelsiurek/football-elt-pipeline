"""Tests for elt/load.py.

load_matches is plain ORM, so it runs against a real in-memory SQLite DB.
load_standings / load_scorers use Postgres-only ON CONFLICT upserts that can't
execute on SQLite, so here we unit-test the row-building logic by stubbing
pg_insert; the real upsert semantics are covered against Postgres in the dbt
integration job (step 4).
"""

from unittest.mock import MagicMock

import load
import models


# ─────────────────────────────────────────
# load_matches — real SQLite
# ─────────────────────────────────────────
def test_load_matches_inserts_all_rows(sqlite_session, matches_payload):
    load.load_matches(matches_payload, sqlite_session)
    assert sqlite_session.query(models.RawMatch).count() == 2


def test_load_matches_skips_duplicates_on_second_run(sqlite_session, matches_payload):
    """The UNIQUE(match_id) constraint + IntegrityError handling means re-running
    the same payload must not create duplicate rows."""
    load.load_matches(matches_payload, sqlite_session)
    load.load_matches(matches_payload, sqlite_session)  # identical data again
    assert sqlite_session.query(models.RawMatch).count() == 2


def test_load_matches_maps_fields_and_parses_date(sqlite_session, matches_payload):
    load.load_matches(matches_payload, sqlite_session)

    finished = sqlite_session.query(models.RawMatch).filter_by(match_id=1001).one()
    assert finished.home_team == "Arsenal FC"
    assert finished.away_team == "Chelsea FC"
    assert finished.home_score == 2
    assert finished.away_score == 1
    assert finished.competition == "Premier League"
    assert finished.season == "2024"
    # utcDate string was parsed into a real datetime
    assert (finished.match_date.year, finished.match_date.month, finished.match_date.day) == (
        2024,
        8,
        17,
    )


def test_load_matches_keeps_null_scores_for_scheduled_games(sqlite_session, matches_payload):
    """Scheduled matches have null scores — they must load as NULL, not 0."""
    load.load_matches(matches_payload, sqlite_session)
    scheduled = sqlite_session.query(models.RawMatch).filter_by(match_id=1002).one()
    assert scheduled.status == "SCHEDULED"
    assert scheduled.home_score is None
    assert scheduled.away_score is None


# ─────────────────────────────────────────
# load_standings / load_scorers — row-building logic (pg_insert stubbed)
# ─────────────────────────────────────────
def _stub_pg_insert(monkeypatch):
    """Replace load.pg_insert with a chainable mock and return it so tests can
    read back the rows passed to .values(...)."""
    insert_mock = MagicMock()
    insert_mock.values.return_value = insert_mock
    insert_mock.on_conflict_do_update.return_value = insert_mock
    monkeypatch.setattr(load, "pg_insert", lambda _model: insert_mock)
    return insert_mock


def test_load_standings_builds_rows_and_stringifies_season(monkeypatch, standings_payload):
    insert_mock = _stub_pg_insert(monkeypatch)
    session = MagicMock()

    load.load_standings(standings_payload, session)

    rows = insert_mock.values.call_args.args[0]
    assert len(rows) == 2
    # season came in as int 2024 -> must be coerced to "2024"
    assert all(row["season"] == "2024" for row in rows)
    assert rows[0]["team"] == "Arsenal FC"
    assert rows[0]["points"] == 25
    assert rows[0]["drawn"] == 1  # API "draw" -> column "drawn"
    session.execute.assert_called_once()
    session.commit.assert_called_once()


def test_load_standings_empty_table_is_a_noop(monkeypatch):
    _stub_pg_insert(monkeypatch)
    session = MagicMock()
    empty = {
        "competition": {"name": "Premier League"},
        "filters": {"season": 2024},
        "standings": [{"table": []}],
    }

    load.load_standings(empty, session)

    session.execute.assert_not_called()
    session.commit.assert_not_called()


def test_load_scorers_defaults_missing_optional_fields_to_none(monkeypatch, scorers_payload):
    insert_mock = _stub_pg_insert(monkeypatch)
    session = MagicMock()

    load.load_scorers(scorers_payload, session)

    rows = insert_mock.values.call_args.args[0]
    palmer = next(row for row in rows if row["player_name"] == "Cole Palmer")
    assert palmer["assists"] is None
    assert palmer["penalties"] is None
    assert palmer["goals"] == 9
    session.execute.assert_called_once()


def test_load_scorers_empty_list_is_a_noop(monkeypatch):
    _stub_pg_insert(monkeypatch)
    session = MagicMock()
    empty = {
        "competition": {"name": "Premier League"},
        "filters": {"season": 2024},
        "scorers": [],
    }

    load.load_scorers(empty, session)

    session.execute.assert_not_called()
