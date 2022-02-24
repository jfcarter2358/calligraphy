.PHONY: help lint test clean

help:  ## Show this help
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

lint:  ## Format and lint the templater script
	black caligraphy
	pylint caligraphy

test:  ## Test the templater script
	coverage run -m pytest -vv
	coverage report
	coverage html

clean:  ## Remove test artifacts
	rm -rf .coverage 
