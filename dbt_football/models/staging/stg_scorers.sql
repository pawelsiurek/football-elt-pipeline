with source as (
    select * from {{ source('raw_football', 'raw_scorers') }}
),

renamed_and_casted as (
    select
        competition,
        season,
        player_name,
        team,
        coalesce(goals::int, 0) as goals,
        coalesce(assists::int, 0) as assists,
        coalesce(penalties::int, 0) as penalties,
        inserted_at
    from source
)

select * from renamed_and_casted
