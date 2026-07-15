"""A small, internally-consistent mini-season used for the dbt + upsert
integration tests.

Every value is hand-checked against the project's data-quality assertions:
  * standings: played == won + drawn + lost
               points == won * 3 + drawn
               goal_difference == goals_for - goals_against
  * scorers:   penalties <= goals, one row per player
  * matches:   FINISHED rows have both scores, home_team != away_team

Shapes mirror football-data.org v4 responses (only the keys the loaders read).
"""

SEASON = "2024"
COMPETITION = "Premier League"


def _standing(name, pos, played, won, drawn, lost, gf, ga, gd, pts):
    return {
        "team": {"name": name},
        "position": pos,
        "playedGames": played,
        "won": won,
        "draw": drawn,
        "lost": lost,
        "goalsFor": gf,
        "goalsAgainst": ga,
        "goalDifference": gd,
        "points": pts,
    }


# 4 teams; each row satisfies played=W+D+L, points=3W+D, gd=gf-ga.
STANDINGS = {
    "competition": {"name": COMPETITION},
    "filters": {"season": SEASON},
    "standings": [
        {
            "table": [
                #          name,           pos, P, W, D, L, GF, GA, GD, Pts
                _standing("Arsenal FC", 1, 3, 3, 0, 0, 8, 2, 6, 9),
                _standing("Chelsea FC", 2, 3, 1, 2, 0, 5, 3, 2, 5),
                _standing("Liverpool FC", 3, 3, 1, 0, 2, 4, 6, -2, 3),
                _standing("Everton FC", 4, 3, 0, 1, 2, 2, 7, -5, 1),
            ]
        }
    ],
}

# Unique players, penalties <= goals; the last one omits the optional keys so the
# loader falls back to None and dbt coalesces to 0.
SCORERS = {
    "competition": {"name": COMPETITION},
    "filters": {"season": SEASON},
    "scorers": [
        {
            "player": {"name": "Bukayo Saka"},
            "team": {"name": "Arsenal FC"},
            "goals": 6,
            "assists": 3,
            "penalties": 1,
        },
        {
            "player": {"name": "Cole Palmer"},
            "team": {"name": "Chelsea FC"},
            "goals": 5,
            "assists": 2,
            "penalties": 2,
        },
        {
            "player": {"name": "Mohamed Salah"},
            "team": {"name": "Liverpool FC"},
            "goals": 4,
            "assists": 1,
            "penalties": 0,
        },
        {
            "player": {"name": "Dominic Calvert-Lewin"},
            "team": {"name": "Everton FC"},
            "goals": 2,
        },
    ],
}


def _match(match_id, matchday, status, home, away, home_score, away_score, utc_date):
    return {
        "id": match_id,
        "matchday": matchday,
        "status": status,
        "homeTeam": {"name": home},
        "awayTeam": {"name": away},
        "score": {"fullTime": {"home": home_score, "away": away_score}},
        "utcDate": utc_date,
    }


# Every team plays >=1 FINISHED game; one SCHEDULED game carries null scores.
MATCHES = {
    "competition": {"name": COMPETITION},
    "filters": {"season": SEASON},
    "matches": [
        _match(2001, 1, "FINISHED", "Arsenal FC", "Everton FC", 3, 0, "2024-08-17T14:00:00Z"),
        _match(2002, 1, "FINISHED", "Chelsea FC", "Liverpool FC", 2, 1, "2024-08-17T16:30:00Z"),
        _match(2003, 2, "FINISHED", "Liverpool FC", "Arsenal FC", 1, 2, "2024-08-24T14:00:00Z"),
        _match(2004, 2, "FINISHED", "Everton FC", "Chelsea FC", 1, 1, "2024-08-24T16:30:00Z"),
        _match(2005, 3, "FINISHED", "Arsenal FC", "Chelsea FC", 2, 1, "2024-08-31T14:00:00Z"),
        _match(2006, 3, "FINISHED", "Liverpool FC", "Everton FC", 3, 1, "2024-08-31T16:30:00Z"),
        _match(
            2007, 4, "SCHEDULED", "Everton FC", "Arsenal FC", None, None, "2024-09-14T14:00:00Z"
        ),
    ],
}
