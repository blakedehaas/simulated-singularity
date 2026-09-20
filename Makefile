PYTHON := .venv/bin/python
PIP_COMPILE := .venv/bin/pip-compile
IMAGE := simulated-singularity:phase1
export CUSTOM_COMPILE_COMMAND := make lock

.PHONY: bootstrap lock check lint format types architecture test compile docs package-check container-check release-check

bootstrap:
	python3.12 -m venv .venv
	$(PYTHON) -m pip install --require-hashes -r requirements-dev.lock
	$(PYTHON) -m pip install --no-deps --no-build-isolation -e .

lock:
	$(PIP_COMPILE) --generate-hashes --strip-extras --allow-unsafe --index-url https://pypi.org/simple --output-file requirements.lock requirements.in
	$(PIP_COMPILE) --generate-hashes --strip-extras --allow-unsafe --index-url https://pypi.org/simple --output-file requirements-build.lock requirements-build.in
	$(PIP_COMPILE) --generate-hashes --strip-extras --allow-unsafe --index-url https://pypi.org/simple --constraint requirements.lock --constraint requirements-build.lock --output-file requirements-dev.lock requirements-dev.in

check: lint format types architecture test compile docs package-check

lint:
	.venv/bin/ruff check src tests scripts

format:
	.venv/bin/ruff format --check src tests scripts

types:
	.venv/bin/mypy --strict

architecture:
	.venv/bin/lint-imports --no-cache

test:
	$(PYTHON) -m pytest

compile:
	$(PYTHON) -m compileall -q -f src tests scripts

docs:
	.venv/bin/mkdocs build --strict

package-check:
	$(PYTHON) -m build --no-isolation
	$(PYTHON) scripts/check_package.py

container-check:
	docker compose config --quiet
	docker build --pull --no-cache --platform linux/amd64 --tag $(IMAGE) .
	docker run --rm --network none $(IMAGE) python -c 'import simulated_singularity'
	docker run --rm --network none $(IMAGE) ss --help
	docker run --rm --network none $(IMAGE) ss doctor
	docker run --rm --network none $(IMAGE) ss doctor --json
	docker image inspect $(IMAGE) --format '{{.Id}}'

release-check: check container-check
