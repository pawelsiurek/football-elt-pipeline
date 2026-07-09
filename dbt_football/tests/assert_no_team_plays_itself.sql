-- A fixture must be between two different teams.
-- Any match where home_team = away_team means the join/parse of the API
-- payload went wrong. Test fails if this query returns any rows.

select
    match_id,
    home_team,
    away_team
from {{ ref('stg_matches') }}
where home_team = away_team