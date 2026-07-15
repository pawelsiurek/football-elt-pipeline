-- A match reported as FINISHED must have both scores recorded.
-- Scheduled/upcoming matches legitimately have NULL scores, so we only
-- police the FINISHED ones. Test fails if any finished match is missing a score.

select
    match_id,
    home_team,
    away_team,
    home_score,
    away_score
from {{ ref('stg_matches') }}
where status = 'FINISHED'
  and (home_score is null or away_score is null)
