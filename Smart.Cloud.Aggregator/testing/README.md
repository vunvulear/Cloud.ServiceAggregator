# Testing Guide

This directory contains all test files for the Smart Cloud Aggregator project.

## Directory Structure

```
testing/
??? __init__.py              # Package initialization
??? test_unit_tests.py       # Comprehensive unit tests (50+ tests)
??? test_aggregator.py       # Integration and functional tests
??? README.md                # This file
```

## Running Tests

### Run All Unit Tests
```bash
python testing/test_unit_tests.py
```

**Expected Output:**
```
======================================================================
TEST SUMMARY
======================================================================
Tests Run:    50
Successes:    50
Failures:     0
Errors:       0
======================================================================
? ALL TESTS PASSED!
```

### Run Functional/Integration Tests
```bash
python testing/test_aggregator.py
```

**Expected Output:**
```
============================================================
SMART CLOUD AGGREGATOR - TEST SUITE
============================================================
...
============================================================
TEST SUMMARY
============================================================
Tests Passed: X/X
============================================================
? ALL TESTS PASSED!
```

### Run Tests with Coverage
```bash
pip install coverage
coverage run -m unittest discover testing
coverage report
coverage html
```

## Test Files Description

### test_unit_tests.py
Comprehensive unit test suite with **50+ test cases** organized into 4 classes:

**TestTerraformParser (15 tests)**
- Parser initialization and validation
- Service mapping checks
- Resource extraction (single & multiple)
- Resource group extraction
- Directory and file parsing
- Error handling

**TestReportGenerator (12 tests)**
- Report generation
- Content validation
- Formatting checks
- Summary calculations
- Edge case handling

**TestIntegration (4 tests)**
- End-to-end workflows
- Multi-file processing
- File output
- JSON export

**TestEdgeCases (6 tests)**
- Malformed input handling
- Nested blocks
- Special characters
- Empty files
- Comment handling

### test_aggregator.py
Integration and functional tests for:
- Basic analysis of Terraform files
- Verbose mode operation
- Error handling (invalid paths)
- Report generation and verification
- JSON output validation

## Test Statistics

| Metric | Value |
|--------|-------|
| Total Tests | 50+ |
| Test Classes | 4 |
| Test Code Lines | 450+ |
| Expected Pass Rate | 100% |
| Execution Time | < 1 second |

## How to Add New Tests

### Unit Test Example

Add to appropriate test class in `test_unit_tests.py`:

```python
def test_new_feature(self):
    """Test description"""
    # Arrange
    test_data = ...
    
    # Act
    result = function_to_test(test_data)
    
    # Assert
    self.assertEqual(result, expected_value)
```

### Run Specific Test

```bash
# Run specific test class
python -m unittest testing.test_unit_tests.TestTerraformParser

# Run specific test method
python -m unittest testing.test_unit_tests.TestTerraformParser.test_extract_single_resource
```

## Test Best Practices Used

? **AAA Pattern** (Arrange-Act-Assert)
? **Test Isolation** (Independent tests)
? **Setup/Teardown** (Proper resource management)
? **Realistic Data** (Real Terraform syntax)
? **Comprehensive Coverage** (Happy path + error cases + edge cases)

## Continuous Integration

Tests are CI/CD compatible and can be run in pipelines:

**GitHub Actions Example:**
```yaml
- name: Run Unit Tests
  run: python testing/test_unit_tests.py
```

## Troubleshooting

### "Module not found" Error
```bash
# Ensure imports use correct path from project root
# From: from Smart.Cloud.Aggregator import ...
# To:   from src.aggregator import ...
```

### "FileNotFoundError" in Tests
```bash
# Run from project root directory
cd Smart.Cloud.Aggregator
python testing/test_unit_tests.py
```

### Tests Taking Too Long
Tests should complete in < 1 second. If slower:
- Check for file system issues
- Verify temp directory permissions
- Look for hanging network calls (shouldn't exist)

## Related Documentation

- **Testing Guide:** See `docs/TESTING_GUIDE.md`
- **Unit Testing Reference:** See `UNIT_TESTING.md`
- **Project Overview:** See `README.md`

---

**Test Suite Version:** 1.0  
**Last Updated:** 2024  
**Status:** Production Ready
