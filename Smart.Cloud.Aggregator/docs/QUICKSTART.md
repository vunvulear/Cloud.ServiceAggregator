# Quick Start Guide

Get Smart Cloud Aggregator running in minutes.

## Prerequisites

- Python 3.10+

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

- Also generate CSV (folder name header + service, resource_type, category):
  ```bash
  python main.py <path-to-infra> --csv
  ```

- JSON only (no markdown):
  ```bash
  python main.py <path-to-infra> --json-only
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

- `cloud_services_report.md`: Markdown report with summary including Azure Services, AWS Services, and Total Resources; vendor-separated sections
- `cloud_services_report.json`: JSON report with `summary` (including `azure_services` and `aws_services`), `metadata`, `services`, and `vendors` grouped by cloud
- `cloud_services_report.csv`: CSV with first line as analyzed folder and rows as `service_name,resource_type,category,vendor`

## Examples

```bash
# Analyze a Terraform/Bicep repo
python main.py ./infrastructure -j --csv -v

# Analyze CloudFormation YAML with JSON output only
python main.py ./cf-templates --json-only
```

## Running tests

```bash
# Run core suite
python -m unittest discover -s testing -p "test_*.py"

# Run with verbosity
python -m unittest discover -s testing -p "test_*.py" -v
```

## Troubleshooting

- Exclude large folders by adding to the scanner’s exclude list in code (`DirectoryScanner.add_excluded_directory`)
