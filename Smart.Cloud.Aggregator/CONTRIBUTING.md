# Contributing to Smart Cloud Aggregator

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Welcome diverse perspectives
- Provide constructive feedback
- Focus on the code, not the person

## Getting Started

### Development Setup

1. **Fork & Clone**
   ```bash
   git clone https://github.com/vunvulear/Cloud.ServiceAggregator.git
   cd Smart.Cloud.Aggregator
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

3. **Set Up Development Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

### Running Tests

```bash
# Run all tests
python -m unittest discover -s testing -p "test_*.py" -v

# Run specific test class
python -m unittest testing.test_v2_unit_tests.TestReportGenerator -v

# Run with coverage
pip install coverage
coverage run -m unittest discover -s testing
coverage report
coverage html  # generates htmlcov/index.html
```

## Contribution Types

### ?? Bug Reports

**Before submitting**, check if the issue already exists.

**When submitting**, include:
- Python version (`python --version`)
- OS (Windows, macOS, Linux)
- Steps to reproduce
- Expected vs actual behavior
- Sample IaC files (if applicable)

### ? Feature Requests

- Describe the feature and use case
- Explain how it benefits users
- Suggest potential implementation approaches

### ?? Documentation

Documentation improvements are always welcome:
- Fix typos and clarify language
- Add examples
- Improve architecture documentation
- Enhance API documentation

### ?? Code Contributions

## Development Guidelines

### Code Style

- Follow PEP 8 conventions
- Use 4 spaces for indentation
- Line length: 100 characters
- Type hints for function parameters and returns

```python
def parse_terraform(file_path: str) -> Dict[str, Any]:
    """Parse Terraform file and extract resources."""
    pass
```

### Testing Requirements

- **All PRs must include tests**
- Maintain test coverage above 85%
- Tests should be in `testing/` directory
- Use descriptive test names: `test_<function>_<scenario>_<expected_result>`

Example:
```python
def test_terraform_parser_extracts_single_resource(self):
    """Test parser extracts resources from valid .tf file"""
    pass

def test_terraform_parser_ignores_non_azure_resources(self):
    """Test parser filters non-Azure resource types"""
    pass
```

### Commit Messages

Follow conventional commits format:

```
feat: add GCP parser support
fix: resolve resource grouping bug
docs: update architecture documentation
test: add tests for vendor filtering
refactor: simplify report generator logic
```

### PR Process

1. **Create Pull Request**
   - Clear title describing the change
   - Reference related issues: `Closes #123`
   - Describe what changed and why
   - Link to relevant documentation

2. **Automated Checks**
   - All tests must pass
   - Code should follow project style

3. **Review Process**
   - At least one approval required
   - Address feedback constructively
   - Keep commits clean and organized

4. **Merge**
   - Use "Squash and merge" for single logical units
   - Use "Create a merge commit" for feature branches
   - Delete head branch after merge

## Areas for Contribution

### High Priority
- [ ] **GCP Support** - Add Google Cloud Platform parser
- [ ] **Policy Compliance** - Add security/compliance checking
- [ ] **Cost Estimation** - Estimate resource costs per cloud
- [ ] **CI/CD Integration** - GitHub Actions, GitLab CI examples

### Medium Priority
- [ ] **Web Dashboard** - Simple UI for report visualization
- [ ] **Terraform State** - Parse `.tfstate` files directly
- [ ] **More Cloud Providers** - Alibaba, IBM, etc.
- [ ] **Performance** - Optimize for large repositories

### Good First Issues
- Documentation improvements
- Test coverage expansion
- Bug fixes
- Small feature enhancements

## Parser Development

Adding a new IaC format? Here's the process:

1. **Create Parser Class**
   ```python
   # src/parsers/your_parser.py
   class YourFormatParser(BaseParser):
       """Parser for your format."""
       
       def parse_file(self, file_path: str) -> Dict[str, Any]:
           """Parse file and return resources."""
           pass
   ```

2. **Add to Universal Scanner**
   - Register language in `src/universal_scanner.py`
   - Add file extension patterns
   - Add language enum value

3. **Create Tests**
   - Unit tests in `testing/`
   - Include valid and invalid samples
   - Test error handling

4. **Update Documentation**
   - Update `docs/SUPPORTED_SERVICES_BY_PARSER.md`
   - Add examples to `docs/QUICKSTART.md`

## Reporting Security Issues

Do **not** open public issues for security vulnerabilities.

Instead, email: security@vunvulear.dev with:
- Vulnerability description
- Affected versions
- Potential impact
- Suggested fix (if any)

## Project Maintainers

- [@vunvulear](https://github.com/vunvulear) - Project Lead

---

Thank you for contributing! Your efforts help make this project better for everyone.
