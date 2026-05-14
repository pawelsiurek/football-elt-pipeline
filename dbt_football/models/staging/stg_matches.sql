with source as (
    select * from {{ source('raw_football', 'raw_matches') }}
),

renamed_and_casted as (
    select
        match_id,
        competition,
        season,
        matchday as match_day,
        status,
        home_team,
        away_team,
        home_score,
        away_score,
        match_date::date as match_date,
        inserted_at
    from source
)

select * from renamed_and_casted