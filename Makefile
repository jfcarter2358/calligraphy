.PHONY: help lint test clean

help:  ## Show this help
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

lint:  ## Format and lint caligraphy
	black caligraphy
	pylint caligraphy

test:  ## Test caligraphy
	pytest --cov=caligraphy --cov-report=html --cov-fail-under=95 -W ignore::DeprecationWarning

clean:  ## Remove test artifacts
	rm -rf .coverage || true
	rm -rf htmlcov || true
	rm -rf .pytest_cache || true
	rm -rf caligraphy/__pycache__ || true
