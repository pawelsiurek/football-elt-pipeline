"""Real-Postgres proof that load_standings / load_scorers UPSERT.

These exercise the Postgres-only `ON CONFLICT DO UPDATE` path that can't run on
SQLite (hence they live here, not in the unit suite). The invariant under test:
re-loading a mutable snapshot must refresh the existing row and insert genuinely
new ones -- never append a duplicate.
"""

from copy import deepcopy

import load
import pytest
from fixtures import SCORERS, STANDINGS
from models import RawScorer, RawStanding

pytestmark = pytest.mark.integration


def test_load_standings_updates_in_place_and_inserts_new(pg_session):
    load.load_standings(STANDINGS, pg_session)
    assert pg_session.query(RawStanding).count() == 4
    assert pg_session.query(RawStanding).filter_by(team="Arsenal FC").one().points == 9

    # Next matchday: Arsenal win again (9 -> 12 pts), and a new team appears.
    later = deepcopy(STANDINGS)
    arsenal = later["standings"][0]["table"][0]
    arsenal["won"], arsenal["playedGames"], arsenal["points"] = 4, 4, 12
    arsenal["goalsFor"], arsenal["goalDifference"] = 10, 8
    later["standings"][0]["table"].append(
        {
            "team": {"name": "Newcastle United FC"},
            "position": 5,
            "playedGames": 4,
            "won": 1,
            "draw": 1,
            "lost": 2,
            "goalsFor": 4,
            "goalsAgainst": 6,
            "goalDifference": -2,
            "points": 4,
        }
    )
    load.load_standings(later, pg_session)

    # 4 existing updated in place + 1 new = 5 rows, NOT 9.
    assert pg_session.query(RawStanding).count() == 5
    assert pg_session.query(RawStanding).filter_by(team="Arsenal FC").one().points == 12
    assert pg_session.query(RawStanding).filter_by(team="Newcastle United FC").one().points == 4


def test_load_scorers_updates_in_place_and_inserts_new(pg_session):
    load.load_scorers(SCORERS, pg_session)
    assert pg_session.query(RawScorer).count() == 4
    assert pg_session.query(RawScorer).filter_by(player_name="Bukayo Saka").one().goals == 6

    later = deepcopy(SCORERS)
    later["scorers"][0]["goals"] = 8  # Saka scores twice more
    later["scorers"].append(
        {"player": {"name": "Erling Haaland"}, "team": {"name": "Chelsea FC"}, "goals": 1}
    )
    load.load_scorers(later, pg_session)

    assert pg_session.query(RawScorer).count() == 5
    assert pg_session.query(RawScorer).filter_by(player_name="Bukayo Saka").one().goals == 8
