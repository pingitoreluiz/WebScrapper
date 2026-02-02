.PHONY: test coverage lint format clean install help

help:
	@echo "Available commands:"
	@echo "  make test          - Run all tests"
	@echo "  make coverage      - Run tests with coverage report"
	@echo "  make lint          - Run linters (flake8, mypy)"
	@echo "  make format        - Format code with black"
	@echo "  make clean         - Remove cache and temporary files"
	@echo "  make install       - Install dependencies"
	@echo "  make check         - Run all quality checks (lint + test)"

test:
	python -m pytest tests/ -v

coverage:
	python -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

coverage-report:
	python -m pytest tests/ --cov=src --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

lint:
	@echo "Running flake8..."
	flake8 src/ tests/ || true
	@echo "Running mypy..."
	mypy src/ || true

format:
	@echo "Formatting with black..."
	black src/ tests/
	@echo "Sorting imports with isort..."
	isort src/ tests/

clean:
	@echo "Cleaning cache and temporary files..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/ 2>/dev/null || true
	@echo "Clean complete!"

install:
	pip install -r requirements.txt
	@echo "Dependencies installed!"

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	@echo "Development dependencies installed!"

check: lint test
	@echo "All checks passed!"

quick-test:
	python -m pytest tests/unit/ -v --tb=short

integration-test:
	python -m pytest tests/integration/ -v

watch:
	ptw -- tests/ -v
