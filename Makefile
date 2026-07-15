.PHONY: help install-dev lint format format-check test ci precommit

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

test:  ## Run the pytest suite (added in step 2)
	pytest

ci:  ## Everything CI's quality+test jobs run, locally
	ruff check .
	ruff format --check .
	pytest

precommit:  ## Run all pre-commit hooks across the whole repo
	pre-commit run --all-files
