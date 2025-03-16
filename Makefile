.PHONY: init-repo-setup poetry-export test lint

init-repo-setup:
	poetry install --all-groups
	pre-commit install

poetry-export-dev:
	poetry export --with dev --without-hashes -f requirements.txt -o requirements.txt

poetry-export-prod:
	poetry export --without-hashes -f requirements.txt -o requirements.txt

test:
	- coverage run -m pytest tests --junit-xml=".junit-report.xml"
	coverage report

lint:
	flake8 cockatoo_chain tests

precommit:
	pre-commit
