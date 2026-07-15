-- goal_difference is a derived field and must always equal
-- goals_for - goals_against. If the source ever ships an inconsistent value
-- (or our cast drops data), this catches it. Test fails on any mismatch.

select
    team,
    goal_difference,
    goals_for,
    goals_against,
    goals_for - goals_against as expected_goal_difference
from {{ ref('stg_standings') }}
where goal_difference <> goals_for - goals_against
