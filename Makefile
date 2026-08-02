.PHONY: install test compile frontend-install frontend-test frontend-build lint security audit validate

install:
	python -m pip install -r backend/requirements-dev.txt
	npm --prefix frontend install

test:
	python -m pytest -q

compile:
	python -m compileall -q backend/app

frontend-install:
	npm --prefix frontend install

frontend-test:
	npm --prefix frontend test

frontend-build:
	npm --prefix frontend run build

lint:
	python scripts/lint.py
	npm --prefix frontend run lint

security:
	python scripts/check_repo.py secrets
	python scripts/check_repo.py sensitive
	python scripts/check_repo.py links

audit:
	python -m pip check
	npm --prefix frontend audit --offline --audit-level=high

validate: test compile frontend-test frontend-build lint security audit
