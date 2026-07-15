"""Populate the raw_* tables with fixture data, then hand off to `dbt build`.

Run as a script (CI does this before dbt build):

    python tests/integration/seed.py

Connection comes from DB_* env vars -- the SAME ones dbt's profile reads -- so
seed and dbt target one database. It intentionally does NOT load a .env file, so
it can only ever touch a Postgres you point it at explicitly (a throwaway/CI DB).
"""

import os
import sys
from pathlib import Path

# elt/ uses flat imports (from models import ...), so put it on the path like the
# Airflow DAG does. fixtures.py sits next to this file and imports as a sibling.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "elt"))

from fixtures import MATCHES, SCORERS, STANDINGS  # noqa: E402
from load import load_matches, load_scorers, load_standings  # noqa: E402
from loguru import logger  # noqa: E402
from models import create_tables  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402


def build_db_url() -> str:
    return (
        f"postgresql+psycopg2://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}"
        f"@{os.environ.get('DB_HOST', 'localhost')}:{os.environ.get('DB_PORT', '5432')}"
        f"/{os.environ['DB_NAME']}"
    )


def main() -> None:
    engine = create_engine(build_db_url())
    create_tables(engine)
    with Session(engine) as session:
        logger.info("Seeding fixture data into raw_* tables...")
        load_matches(MATCHES, session)
        load_standings(STANDINGS, session)
        load_scorers(SCORERS, session)
        logger.info("Seed complete.")


if __name__ == "__main__":
    main()
