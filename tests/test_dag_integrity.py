"""Airflow DAG integrity checks.

These load the DAG through Airflow's DagBag (the same machinery the scheduler
uses) and assert it parses cleanly with the expected shape. Catches import
errors, typos, and broken task wiring without running Airflow.

Airflow isn't installed locally (it doesn't run natively on Windows), so this
whole module is skipped unless Airflow is importable — i.e. it runs for real in
CI on Linux, and is a no-op on the dev machine.
"""

import os
import tempfile
from pathlib import Path

import pytest

# Airflow initialises config/state on import, so point it at a throwaway home and
# keep it out of the DB — must be set before airflow is imported below.
os.environ.setdefault("AIRFLOW_HOME", tempfile.mkdtemp(prefix="airflow_test_"))
os.environ.setdefault("AIRFLOW__CORE__LOAD_EXAMPLES", "False")
os.environ.setdefault("AIRFLOW__CORE__UNIT_TEST_MODE", "True")

airflow_models = pytest.importorskip(
    "airflow.models",
    reason="Airflow not installed (no native Windows support); this runs in CI.",
)
DagBag = airflow_models.DagBag

DAGS_DIR = Path(__file__).resolve().parent.parent / "dags"
DAG_ID = "football_elt_pipeline"
EXPECTED_TASKS = {
    "db_initialization",
    "sync_matches",
    "sync_standings",
    "sync_scorers",
    "dbt_run",
    "dbt_test",
}


def _dagbag() -> "DagBag":
    return DagBag(dag_folder=str(DAGS_DIR), include_examples=False)


def test_dagbag_has_no_import_errors():
    dagbag = _dagbag()
    assert dagbag.import_errors == {}, f"DAG import errors: {dagbag.import_errors}"


def test_expected_dag_is_present():
    assert DAG_ID in _dagbag().dag_ids


def test_dag_has_expected_tasks():
    dag = _dagbag().dags[DAG_ID]
    assert dag is not None
    assert set(dag.task_ids) == EXPECTED_TASKS


def test_dag_task_wiring():
    """db_init fans out to the three syncs, which converge on dbt_run -> dbt_test."""
    dag = _dagbag().dags[DAG_ID]

    db_init = dag.get_task("db_initialization")
    assert {t.task_id for t in db_init.downstream_list} == {
        "sync_matches",
        "sync_standings",
        "sync_scorers",
    }

    dbt_run = dag.get_task("dbt_run")
    assert {t.task_id for t in dbt_run.downstream_list} == {"dbt_test"}
    assert dbt_run.downstream_list[0].downstream_list == []  # dbt_test is terminal
