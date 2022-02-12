PY ?= python3

.PHONY: test coverage install install-dev install-ci

test:
	$(PY) -m pytest tests/

test-ci:
	$(PY) -m pytest -vv tests/

coverage:
	$(PY) -m pytest . --cov cptk/ --cov-report xml --cov-report term

install:
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install .

install-dev:
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r requirements-dev.txt
	$(PY) -m pip install -e .

install-ci:
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r requirements-dev.txt
	$(PY) -m pip install .

# TODO: add 'build' and 'upload' tasks
