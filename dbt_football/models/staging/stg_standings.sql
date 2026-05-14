with source as (
    select * from {{ source('raw_football', 'raw_standings') }}
),

renamed_and_casted as (
    select
        competition,
        season,
        team,
        coalesce(position::int, 0) as position,
        coalesce(played::int, 0) as played,
        coalesce(won::int, 0) as won,
        coalesce(drawn::int, 0) as drawn,
        coalesce(lost::int, 0) as lost,
        coalesce(goals_for::int, 0) as goals_for,
        coalesce(goals_against::int, 0) as goals_against,
        coalesce(goal_difference::int, 0) as goal_difference,
        coalesce(points::int, 0) as points,
        inserted_at
    from source
)

select * from renamed_and_casted