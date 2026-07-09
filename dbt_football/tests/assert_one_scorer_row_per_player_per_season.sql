-- The grain of scorers is (competition, season, player_name): one row per
-- player per season. Duplicates here mean the load appended instead of
-- upserting. Test fails if any group has > 1 row.

select
    competition,
    season,
    player_name,
    count(*) as row_count
from {{ ref('stg_scorers') }}
group by competition, season, player_name
having count(*) > 1
