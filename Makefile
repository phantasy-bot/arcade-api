.PHONY: help install test lint format typecheck clean

# Variables
PYTHON = python
PIP = pip
PYTEST = pytest
BLACK = black
ISORT = isort
FLAKE8 = flake8
MYPY = mypy

# Help
help:
	@echo "Available commands:"
	@echo "  make install      Install development dependencies"
	@echo "  make test         Run tests with coverage"
	@echo "  make test-fast    Run tests without coverage"
	@echo "  make lint         Run code linter"
	@echo "  make format       Format code with black and isort"
	@echo "  make typecheck    Run type checking with mypy"
	@echo "  make check        Run all checks (lint, format, typecheck, test)"
	@echo "  make clean        Clean up temporary files"

# Installation
install:
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -e .[dev]

# Testing
test:
	$(PYTEST) --cov=. --cov-report=term-missing --cov-fail-under=80

test-fast:
	$(PYTEST) -v

# Linting and Formatting
lint:
	$(FLAKE8) .

	$(BLACK) --check .
	$(ISORT) --check-only .


format:
	$(BLACK) .
	$(ISORT) .


typecheck:
	$(MYPY) .

# Run all checks
check: lint format typecheck test

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*~" -delete
	find . -type f -name "*.bak" -delete
	del /s /q *.pyc *.pyo *~ *.bak 2>nul || true

dev:
	uvicorn app:app --reload --port 4444

.PHONY: help install test lint format typecheck clean dev
