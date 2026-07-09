with matches as (
    -- Form is computed from results, so only FINISHED matches count (scheduled
    -- matches have NULL scores and would otherwise be miscounted as losses).
    -- Scope to the latest season that has finished matches.
    select * from {{ ref('stg_matches') }}
    where status = 'FINISHED'
      and season = (
          select max(season)
          from {{ ref('stg_matches') }}
          where status = 'FINISHED'
      )
),

-- unpivot: each match appears twice, once for home team once for away team
team_matches as (
    select
        match_id,
        match_date,
        match_day,
        home_team                    as team,
        home_score                   as goals_scored,
        away_score                   as goals_conceded,
        case
            when home_score > away_score then 'W'
            when home_score = away_score then 'D'
            else 'L'
        end                          as result,
        case
            when home_score > away_score then 3
            when home_score = away_score then 1
            else 0
        end                          as points_earned,
        'HOME'                       as venue
    from matches

    union all

    select
        match_id,
        match_date,
        match_day,
        away_team                    as team,
        away_score                   as goals_scored,
        home_score                   as goals_conceded,
        case
            when away_score > home_score then 'W'
            when away_score = home_score then 'D'
            else 'L'
        end                          as result,
        case
            when away_score > home_score then 3
            when away_score = home_score then 1
            else 0
        end                          as points_earned,
        'AWAY'                       as venue
    from matches
),

-- rank each team's matches by date to get last 5
ranked as (
    select
        *,
        row_number() over (
            partition by team
            order by match_date desc
        )                            as match_recency
    from team_matches
),

-- last 5 matches per team
last_5 as (
    select * from ranked
    where match_recency <= 5
),

-- aggregate form over last 5
form as (
    select
        team,
        count(*)                                                    as games_in_form,
        sum(points_earned)                                          as form_points,
        count(*) filter (where result = 'W')                        as form_wins,
        count(*) filter (where result = 'D')                        as form_draws,
        count(*) filter (where result = 'L')                        as form_losses,
        sum(goals_scored)                                           as form_goals_scored,
        sum(goals_conceded)                                         as form_goals_conceded,
        -- string form like W W D L W
        string_agg(result, ' ' order by match_recency desc)        as form_string
    from last_5
    group by team
),

-- full season stats per team
season as (
    select
        team,
        count(*)                                                    as total_played,
        sum(points_earned)                                          as total_points,
        sum(goals_scored)                                           as total_goals_scored,
        sum(goals_conceded)                                         as total_goals_conceded,
        count(*) filter (where venue = 'HOME')                      as home_played,
        sum(points_earned) filter (where venue = 'HOME')            as home_points,
        count(*) filter (where venue = 'AWAY')                      as away_played,
        sum(points_earned) filter (where venue = 'AWAY')            as away_points
    from team_matches
    group by team
)

select
    s.team,
    s.total_points,
    s.total_played,
    s.total_goals_scored,
    s.total_goals_conceded,
    s.total_goals_scored - s.total_goals_conceded       as season_goal_difference,
    round(s.total_points::numeric / nullif(s.total_played, 0), 2) as points_per_game,

    -- home vs away split
    s.home_points,
    s.away_points,

    -- form
    f.form_points,
    f.form_wins,
    f.form_draws,
    f.form_losses,
    f.form_goals_scored,
    f.form_goals_conceded,
    f.form_string

from season s
join form f on s.team = f.team
order by s.total_points desc