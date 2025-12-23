# Smart Cloud Aggregator - Installation & Deployment

## System Requirements

- **Python**: 3.10 or higher
- **OS**: Linux, macOS, Windows
- **RAM**: 256MB minimum (1GB+ for large repositories)
- **Disk**: 100MB for installation + space for generated reports

## Installation Methods

### Method 1: From Source (Recommended for Development)

```bash
# Clone repository
git clone https://github.com/vunvulear/Cloud.ServiceAggregator.git
cd Smart.Cloud.Aggregator

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Verify Python version
python --version  # Should be 3.10+

# Run the application
python main.py --help
```

### Method 2: Docker (Coming Soon)

```bash
docker pull ghcr.io/vunvulear/cloud-service-aggregator:latest
docker run -v $(pwd):/data cloud-service-aggregator -v
```

### Method 3: Package Installation (Coming Soon)

```bash
pip install cloud-service-aggregator
cloud-service-aggregator ./my-infrastructure
```

## Quick Start

### Basic Analysis

```bash
# Analyze current directory
python main.py

# Analyze specific directory
python main.py /path/to/infrastructure

# Save to custom output
python main.py ./infra -o my-report.md
```

### Generate Reports

```bash
# Markdown only (default)
python main.py ./infra

# Markdown + JSON
python main.py ./infra -j

# JSON only
python main.py ./infra --json-only

# Verbose output for debugging
python main.py ./infra -v
```

### Analyze Single Language

```bash
# Terraform only
python main.py ./infra --language terraform

# Bicep only
python main.py ./infra --language bicep

# CloudFormation only
python main.py ./infra --language cloudformation
```

## Configuration

### Environment Variables

```bash
# Set Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Windows:
set PYTHONPATH=%PYTHONPATH%;%cd%
```

### Command Line Options

```
Usage: main.py [OPTIONS] [DIRECTORY]

Options:
  -o, --output FILE        Output markdown file name (default: cloud_services_report.md)
  -j, --json              Also generate JSON report
  --json-only             Only generate JSON report (no markdown)
  -v, --verbose           Enable verbose output
  --scan-only             Only scan files, don't parse
  --language LANG         Limit to specific language:
                          terraform, bicep, powershell, cli, arm,
                          cloudformation, python, typescript, go, dotnet, bash
  --recursive             Recursive scan (default: enabled)
  --no-recursive          Disable recursive scan
  -h, --help              Show help message
```

## Output

Reports are generated in:
```
<analyzed-directory>/Smart.Cloud.Aggregator.Output/
??? cloud_services_report.md   # Markdown report
??? cloud_services_report.json # JSON report (if -j flag used)
```

### Report Contents

**Markdown Report:**
- Cloud Services Assessment Report
- Analysis metadata
- Summary statistics
- Services grouped by vendor (Azure, AWS)
- Detailed resource list

**JSON Report:**
- Timestamp
- Summary statistics
- Metadata
- Services (by category)
- Vendors (by cloud provider)

## Troubleshooting

### Python Version Error
```
Error: Python 3.10+ required
Solution: python --version  # Check version
         python -m venv venv  # Use specific Python version
```

### Module Not Found
```
Solution: 
1. Ensure you're in the project root directory
2. export PYTHONPATH=$(pwd)  # Linux/macOS
3. set PYTHONPATH=%cd%       # Windows
```

### No Resources Found
```
Possible causes:
1. Directory has no IaC files
2. Wrong file extensions (ensure .tf, .bicep, .json, etc.)
3. Unsupported format

Solution: Use -v flag to see which files were detected
         python main.py ./infra -v
```

### Permission Denied
```
Solution:
1. Check read permissions: ls -l <directory>
2. Check write permissions for output: chmod 755 <directory>
3. Run with sudo (if necessary, but not recommended)
```

## Integration Examples

### CI/CD Pipeline

**GitHub Actions**
```yaml
name: Infrastructure Analysis

on: [push, pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: python main.py ./infrastructure -j -v
      - uses: actions/upload-artifact@v3
        with:
          name: infrastructure-report
          path: infrastructure/Smart.Cloud.Aggregator.Output/
```

**GitLab CI**
```yaml
analyze-infrastructure:
  image: python:3.10
  script:
    - python main.py ./infrastructure -j -v
  artifacts:
    paths:
      - infrastructure/Smart.Cloud.Aggregator.Output/
    reports:
      dotenv: build.env
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

python main.py ./infrastructure -j -v
if [ $? -ne 0 ]; then
    echo "Infrastructure analysis failed!"
    exit 1
fi
```

## Performance Tips

1. **Exclude unnecessary directories**
   - Analyze only IaC directories when possible
   - Skip build, cache, and node_modules folders

2. **Use language filters**
   - Analyze only specific languages: `--language terraform`
   - Faster than scanning all formats

3. **Monitor verbose output**
   - Use `-v` flag to identify slow operations
   - Check for large number of files

## Uninstallation

```bash
# Remove source code
rm -rf Smart.Cloud.Aggregator

# Remove virtual environment (if created)
rm -rf venv

# Remove generated reports
find . -name "Smart.Cloud.Aggregator.Output" -type d -exec rm -rf {} +
```

## Getting Help

- **Documentation**: See `/docs` folder
- **Issues**: [GitHub Issues](https://github.com/vunvulear/Cloud.ServiceAggregator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/vunvulear/Cloud.ServiceAggregator/discussions)

## Next Steps

1. Read the [Quick Start Guide](docs/QUICKSTART.md)
2. Review [Architecture Overview](docs/ARCHITECTURE.md)
3. Check [Supported Services](docs/SUPPORTED_SERVICES_BY_PARSER.md)
4. Run tests: `python -m unittest discover -s testing -p "test_*.py"`
