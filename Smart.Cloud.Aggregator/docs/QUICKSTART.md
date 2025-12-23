# Quick Start Guide

Get Smart Cloud Aggregator running in minutes.

## Prerequisites

- Python 3.9+
- Optional: PyYAML (improves CloudFormation YAML parsing)

## Install

- Clone the repo and cd into project root
- No extra installs required for basic usage

## Basic usage

- Analyze a folder (all supported formats):
  ```bash
  python main.py <path-to-infra>
  ```

- Also generate JSON:
  ```bash
  python main.py <path-to-infra> -j
  ```

- Verbose output:
  ```bash
  python main.py <path-to-infra> -v
  ```

- Scan only (no parsing):
  ```bash
  python main.py <path-to-infra> --scan-only
  ```

- Limit to one language (example Terraform):
  ```bash
  python main.py <path-to-infra> --language terraform
  ```

## Supported formats

- Azure: Bicep (.bicep), ARM (.json), Terraform (azurerm_*), PowerShell (.ps1), Azure CLI in Bash (.sh)
- AWS: Terraform (aws_*), CloudFormation (JSON/YAML), Bash (aws cli), Python (boto3), TypeScript/Go/Java/C# (SDK/CDK)

## Outputs

- `azure_services_report.md` and `azure_services_report.json` in the working directory
- `docs/SUPPORTED_SERVICES_BY_PARSER.md` — run `scripts/generate_supported_services_by_parser.py` to regenerate

## Examples

```bash
# Analyze a Terraform/Bicep repo
python main.py ./infrastructure -j -v

# Analyze CloudFormation YAML with JSON output only
python main.py ./cf-templates --json-only
```

## Running tests

```bash
# Run core suite
python -m unittest discover -s testing -p "test_*.py"

# Run a specific file
python testing/test_universal_scanner.py
```

## Troubleshooting

- If CloudFormation YAML isn’t picked up, install PyYAML: `pip install pyyaml`
- Exclude large folders by adding to the scanner’s exclude list in code (`DirectoryScanner.add_excluded_directory`)
