# Testing Guide

This directory contains all test files for the Smart Cloud Aggregator project.

## Directory Structure

```
testing/
  __init__.py
  test_*.py
  README.md
```

## Running Tests

- **Run all tests:**

  ```bash
  python -m unittest discover -s testing -p "test_*.py"
  ```

- **Run a specific test file:**

  ```bash
  python testing/test_universal_scanner.py
  ```

- **With verbosity:**

  ```bash
  python -m unittest discover -s testing -p "test_*.py" -v
  ```

## Coverage (optional)

```bash
# Install coverage tool
pip install coverage

# Run tests with coverage
coverage run -m unittest discover -s testing

# View coverage report
coverage report

# Generate HTML report
coverage html
# Open htmlcov/index.html in browser
```

## Notes

- Tests exercise parsing across Terraform, Bicep, ARM, PowerShell, Azure CLI, and AWS languages (CloudFormation, bash, python, typescript, go, java/c#).
- The suite includes integration tests for unified parsers, scanner behavior, and report generation.
