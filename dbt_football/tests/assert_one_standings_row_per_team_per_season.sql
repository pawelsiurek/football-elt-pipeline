-- The grain of standings is (competition, season, team): a team should have
-- exactly one row per season. More than one means the upsert key is wrong or
-- duplicate rows slipped in. Test fails if any group has > 1 row.

select
    competition,
    season,
    team,
    count(*) as row_count
from {{ ref('stg_standings') }}
group by competition, season, team
having count(*) > 1
