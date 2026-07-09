-- Football scoring: 3 points per win, 1 per draw, 0 per loss.
-- So points must equal (won * 3) + drawn.
--
-- Real-world caveat: leagues occasionally apply administrative POINT
-- DEDUCTIONS (e.g. FFP breaches), which would legitimately break this
-- identity. If that ever happens this test will flag it — at which point
-- the source data should be inspected rather than the test silently loosened.

select
    team,
    points,
    won,
    drawn,
    (won * 3) + drawn as expected_points
from {{ ref('stg_standings') }}
where points <> (won * 3) + drawn