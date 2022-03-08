.PHONY: help lint test clean install install-dev docs

help:  ##        Show this help
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

install:  ##     Install poetry if needed and use it to install calligraphy
	pip install poetry
	poetry install --no-dev

install-dev:  ## Install poetry if needed and use it to install calligraphy and dev dependencies
	pip install poetry
	poetry install

lint:  ##        Format and lint calligraphy
	black calligraphy_scripting
	pylint calligraphy_scripting

test:  ##        Test calligraphy
	pytest --cov=calligraphy_scripting --cov-report=html --cov-fail-under=95 -W ignore::DeprecationWarning -vv

clean:  ##       Remove test and doc artifacts
	rm -rf .coverage || true
	rm -rf htmlcov || true
	rm -rf .pytest_cache || true
	rm -rf calligraphy_scripting/__pycache__ || true
	rm -rf tests/__pycache__ || true
	rm -rf docs/build || true

docs:  ##        Generate documentation for calligraphy
	cd docs && make html

release:  ##        Release the current version of calligraphy
	poetry build
	poetry publish
