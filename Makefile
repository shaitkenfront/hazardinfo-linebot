.PHONY: test test-coverage test-watch install clean lint format

# Install dependencies
install:
	python3 -m pip install -r requirements.txt

# Run tests
test:
	python3 -m pytest -v

# Run tests with coverage
test-coverage:
	python3 -m pytest --cov=app --cov-report=term-missing --cov-report=html

# Run tests in watch mode
test-watch:
	python3 -m pytest -f

# Clean up generated files
clean:
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	rm -rf app/__pycache__/
	rm -rf tests/__pycache__/
	rm -f .coverage
	rm -f coverage.xml

# Run linter (if you want to add linting)
lint:
	@echo "No linter configured. Consider adding flake8 or black."

# Format code (if you want to add formatting)
format:
	@echo "No formatter configured. Consider adding black or autopep8."