-- A team can earn at most 3 points in a single game, so points_per_game in
-- the mart can never exceed 3. A value above 3 means either the aggregation
-- or the games-played denominator is wrong. Test fails on any offending team.

select
    team,
    points,
    played,
    points_per_game
from {{ ref('mart_standings') }}
where points_per_game > 3
