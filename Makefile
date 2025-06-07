# Makefile for pyomgmatch development

.PHONY: help install install-dev build test test-cov lint format security clean all

# Default target
help:
	@echo "Available targets:"
	@echo "  install     - Install production dependencies"
	@echo "  install-dev - Install development dependencies"
	@echo "  build       - Build native libraries and package"
	@echo "  test        - Run tests"
	@echo "  test-cov    - Run tests with coverage"
	@echo "  lint        - Run all linting checks"
	@echo "  format      - Format code with black and isort"
	@echo "  security    - Run security scans"
	@echo "  clean       - Clean build artifacts"
	@echo "  all         - Run format, lint, test, and build"

# Install production dependencies
install:
	pip install -r requirements.txt

# Install development dependencies
install-dev: install
	pip install -r requirements-dev.txt

# Build native libraries and package
build:
	./build.sh

# Run tests
test:
	pytest tests/ -v

# Run tests with coverage
test-cov:
	pytest tests/ -v --cov=omg --cov-report=term --cov-report=html

# Run all linting checks
lint:
	@echo "Running flake8..."
	flake8 omg/ tests/
	@echo "Running mypy..."
	mypy omg/ --ignore-missing-imports
	@echo "Checking black formatting..."
	black --check omg/ tests/
	@echo "Checking isort..."
	isort --check-only omg/ tests/

# Format code
format:
	@echo "Formatting with black..."
	black omg/ tests/
	@echo "Sorting imports with isort..."
	isort omg/ tests/

# Run security scans
security:
	@echo "Running bandit..."
	bandit -r omg/
	@echo "Running safety..."
	safety check

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf omg/native/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run all checks and build
all: format lint test build
