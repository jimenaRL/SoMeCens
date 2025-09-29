# Variables
SOURCE = somecens

# Functions
define clean
	rm -rf test/.pytest_cache
	find . -name __pycache__ -type d | xargs rm -rf
endef

# Commands
test: func
all: lint test

clean:
	$(call clean)

deps:
	pip3 install -U pip
	pip3 install -r requirements.txt

lint:
	@echo Linting source code using pep8...
	pycodestyle --ignore E501,E722,E731,E741,W503,W504 $(SOURCE) test
	@echo
	@echo Searching for unused imports...
	importchecker $(SOURCE) | grep -v __init__ || true
	importchecker test | grep -v __init__ || true
	@echo

func:
	@echo Running functional tests...
	PYTHONHASHSEED=0 && pytest -s
	@echo
