-- Penalty goals are a subset of a player's total goals, so penalties can
-- never exceed goals. A violation means the two fields were mismapped from
-- the API payload. Test fails if any scorer has penalties > goals.

select
    player_name,
    team,
    goals,
    penalties
from {{ ref('stg_scorers') }}
where penalties > goals
