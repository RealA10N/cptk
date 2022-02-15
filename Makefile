PY ?= python3

.PHONY: test
test:
	$(PY) -m pytest tests/


.PHONY: test-ci
test-ci:
	$(PY) -m pytest -vv tests/


.PHONY: coverage
coverage:
	$(PY) -m pytest -vv tests/ --cov cptk/ --cov-report xml --cov-report term


.PHONY: install
install:
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install .


.PHONY: install-dev
install-dev:
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r requirements-dev.txt
	$(PY) -m pip install -e .


.PHONY: install-ci
install-ci:
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r requirements-dev.txt
	$(PY) -m pip install .

build: test
	$(PY) setup.py sdist bdist_wheel

upload: build
	$(PY) -m twine upload dist/*
