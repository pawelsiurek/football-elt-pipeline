.PHONY: help install-dev lint format format-check test dbt-parse ci precommit \
        seed dbt-build test-integration integration

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-14s %s\n", $$1, $$2}'

install-dev:  ## Install dev tooling and register the git pre-commit hook
	pip install -r requirements-dev.txt
	pre-commit install

lint:  ## Ruff lint (with autofix)
	ruff check --fix .

format:  ## Ruff format (rewrites files)
	ruff format .

format-check:  ## Ruff format check (no writes) — this is what CI runs
	ruff format --check .

test:  ## Run the fast unit tests (no database)
	pytest -m "not integration"

dbt-parse:  ## Validate dbt models/refs compile (renders profile, no DB connection)
	cd dbt_football && DB_USER=dummy DB_PASSWORD=dummy DB_NAME=dummy \
		dbt parse --profiles-dir .

ci:  ## Everything CI's quality+test jobs run, locally
	ruff check .
	ruff format --check .
	pytest -m "not integration"
	$(MAKE) dbt-parse

# ── Integration flow (needs a THROWAWAY Postgres via DB_* + TEST_DATABASE_URL) ──
seed:  ## Load fixture data into raw_* (uses DB_* env)
	python tests/integration/seed.py

dbt-build:  ## Run dbt build — materialises models AND runs every dbt test
	cd dbt_football && dbt build --profiles-dir .

test-integration:  ## Postgres-backed upsert tests (uses TEST_DATABASE_URL)
	pytest -m integration

integration: seed dbt-build test-integration  ## Full integration run: seed -> dbt build -> upsert tests

precommit:  ## Run all pre-commit hooks across the whole repo
	pre-commit run --all-files
