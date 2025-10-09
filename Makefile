# Variables
SOURCE = somecens

# Functions
define clean
	rm -rf test/.pytest_cache
	find . -name __pycache__ -type d | xargs rm -rf
endef

# Commands
test: func
lint: imports pep8
all: lint test

clean:
	$(call clean)

deps:
	pip3 install -U pip
	pip3 install -r requirements.txt

pep8:
	@echo Linting source code using pep8...
	pycodestyle --ignore E501,E722,E731,E741,W503,W504 $(SOURCE) test

imports:
	@echo Searching for unused imports...
	importchecker $(SOURCE) | grep -v __init__ || true
	importchecker test | grep -v __init__ || true

func:
	@echo Running functional tests...
	PYTHONHASHSEED=0 && pytest -s
	@echo
