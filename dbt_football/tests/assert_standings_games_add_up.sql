-- Every game played resolves to exactly one of win / draw / loss, so
-- played must equal won + drawn + lost. A mismatch means the standings
-- payload was parsed incorrectly. Test fails if any row breaks the identity.

select
    team,
    played,
    won,
    drawn,
    lost
from {{ ref('stg_standings') }}
where played <> won + drawn + lost