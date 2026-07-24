PYTHON ?= python3.12
VENV ?= .venv

.PHONY: setup dev benchmark test seed run-round runner-build format lint clean-start

setup:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/python -m pip install -e ".[dev]"
	cd apps/web && npm ci
	$(VENV)/bin/alembic upgrade head
	$(VENV)/bin/agent-arena seed

dev:
	$(VENV)/bin/python scripts/dev.py

benchmark:
	$(VENV)/bin/python scripts/benchmark.py

test:
	$(VENV)/bin/ruff format --check apps packages scripts tests
	$(VENV)/bin/ruff check apps packages scripts tests
	$(VENV)/bin/pytest
	cd apps/web && npm run lint && npm run typecheck && npm test -- --run && npm run build

seed:
	$(VENV)/bin/agent-arena seed

run-round:
	$(VENV)/bin/agent-arena run-round

runner-build:
	docker build -f packages/agent_runner/Dockerfile -t agent-arena-runner:py312-v1 .

format:
	$(VENV)/bin/ruff format apps packages tests

lint:
	$(VENV)/bin/ruff check apps packages tests

clean-start:
	$(VENV)/bin/python scripts/startup_check.py
