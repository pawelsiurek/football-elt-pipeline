with standings as (
    select * from {{ ref('stg_standings') }}
    -- raw_standings keeps full season history; the current table is the latest
    -- season that has actually kicked off (played > 0), so a fixture-only
    -- pre-season doesn't blank out the mart.
    where season = (
        select max(season)
        from {{ ref('stg_standings') }}
        where played > 0
    )
)

select
    rank() over (order by points desc, goal_difference desc) as league_position,
    team,
    played,
    won,
    drawn,
    lost,
    goals_for,
    goals_against,
    goal_difference,
    points,

    round(points::numeric / nullif(played, 0), 2)       as points_per_game,
    round(won::numeric / nullif(played, 0) * 100, 1)    as win_percentage,
    round(goals_for::numeric / nullif(played, 0), 2)    as goals_per_game

from standings
order by league_position

