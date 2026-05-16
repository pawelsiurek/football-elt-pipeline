with standings as (
    select * from {{ ref('stg_standings') }}
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

