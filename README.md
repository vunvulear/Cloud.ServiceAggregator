# Smart Cloud Aggregator

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen)

Multi-cloud Infrastructure as Code (IaC) analyzer for Azure and AWS that aggregates and reports on cloud services across multiple formats.

## Features

- Multi-Format Support: Terraform, Bicep, ARM Templates, PowerShell, Azure CLI, CloudFormation, and code-based IaC (Python, TypeScript, Go, Java/C#)
- Multi-Cloud: Analyzes both Azure and AWS resources in a single pass
- Vendor Grouping: Services organized and reported separately by cloud vendor (JSON includes a vendors section)
- Multiple Outputs: Markdown, JSON, and CSV reports
- Markdown Summary: Includes counts for both Azure and AWS services, and total resources
- CSV Export: First line is analyzed folder; subsequent lines are service_name, resource_type, category
- Language Detection: Automatically discovers and parses IaC files recursively
- Resource Aggregation: Groups resources by category, service, and cloud vendor

## Installation

### Requirements
- Python 3.10+

### Setup

```bash
git clone https://github.com/vunvulear/Cloud.ServiceAggregator.git
cd Smart.Cloud.Aggregator

# Optional: Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# No external dependencies required for core functionality
```

## Quick Start

### Basic Usage

```bash
# Analyze current directory
python main.py

# Analyze specific directory
python main.py ./my-infrastructure

# Generate JSON report
python main.py ./my-infrastructure -j

# Generate JSON + CSV
python main.py ./my-infrastructure -j --csv

# Verbose output
python main.py ./my-infrastructure -v

# JSON only (no markdown)
python main.py ./my-infrastructure --json-only
```

### Output

Reports are generated in the analyzed directory under `Smart.Cloud.Aggregator.Output/`:

- cloud_services_report.md - Markdown report with vendor-separated sections. Summary shows Azure Services, AWS Services, Total Resources.
- cloud_services_report.json - JSON report with summary, metadata, services, and a vendors section grouped by cloud
- cloud_services_report.csv - CSV report with:
  - Line 1: absolute path of analyzed folder
  - Lines 2..n: service_name,resource_type,category,vendor

## Supported Languages and Formats

### Infrastructure as Code
| Language | Format | Parser | Cloud |
|----------|--------|--------|-------|
| Terraform | .tf | UnifiedIaCParser | Azure, AWS, GCP |
| Bicep | .bicep | BicepParser | Azure |
| ARM Templates | .json | ARMParser | Azure |
| PowerShell | .ps1 | PowerShellParser | Azure |
| Azure CLI | .sh | AzureCliParser | Azure |
| CloudFormation | .yaml, .json | CloudFormationParser | AWS |

### Code-Based IaC
| Language | Format | Detection | Cloud |
|----------|--------|-----------|-------|
| Python | .py | AWS SDK imports | AWS |
| TypeScript | .ts, .tsx | AWS CDK/SDK imports | AWS |
| Go | .go | AWS SDK imports | AWS |
| Java/C# | .java, .cs | AWS SDK imports | AWS |

## Documentation

- Quick Start Guide: docs/QUICKSTART.md
- Architecture Overview: docs/ARCHITECTURE.md
- Universal Scanner Guide: docs/UNIVERSAL_SCANNER_GUIDE.md
- Testing Guide: docs/TESTING_GUIDE.md
- Supported Services: docs/SUPPORTED_SERVICES_BY_PARSER.md

## Project Structure

```
Smart.Cloud.Aggregator/
??? main.py                          # CLI entry point
??? src/
?   ??? azure/
?   ?   ??? parsers/                # Azure-specific parsers
?   ??? aws/
?   ?   ??? parsers/                # AWS-specific parsers
?   ??? service_mapping.py          # Resource type ? service category mapping
?   ??? universal_scanner.py        # Language-aware file discovery
?   ??? enhanced_unified_parser.py  # Multi-cloud unified parser
?   ??? report_generator.py         # Markdown/JSON/CSV report generation
??? docs/                            # Documentation
??? testing/                         # Unit and integration tests
??? scripts/                         # Utility scripts
??? README.md                        # This file
```

## Example Output

### Markdown Report
Reports are organized by cloud vendor with service groupings and a summary including Azure and AWS counts:

```markdown
# Cloud Services Assessment Report

## Summary
- Total Service Categories: N
- Total Azure Services: X
- Total AWS Services: Y
- Total Resources: Z

## Services by Cloud Vendor

### Azure
#### Security
- Role Assignment (azurerm_role_assignment): 2 resources
- Key Vault (azurerm_key_vault): 1 resource

### AWS
#### Security
- IAM Role (aws_iam_role): 6 resources
- KMS Key (aws_kms_key): 2 resources
```

### JSON Report
Includes detailed vendor grouping and summary fields:

```json
{
  "summary": {
    "categories": 9,
    "services": 45,
    "resources": 92,
    "azure_services": 13,
    "aws_services": 32
  },
  "vendors": {
    "Azure": {
      "Security": { ... },
      "Compute": { ... }
    },
    "AWS": {
      "Security": { ... },
      "Compute": { ... }
    }
  }
}
```

### CSV Report
First line is the analyzed folder; subsequent lines contain service_name,resource_type,category.

## Testing

Run all tests with verbose output:

```bash
cd Smart.Cloud.Aggregator
python -m unittest discover -s testing -p "test_*.py" -v
```

Test Coverage:
- 170+ unit and integration tests
- Terraform, Bicep, ARM Templates, CloudFormation parsing
- Report generation (Markdown/JSON/CSV)
- Service mapping validation
- End-to-end workflows

## Troubleshooting

- No resources found: Ensure your directory contains supported IaC files and correct extensions (.tf, .bicep, .json). Use -v to see detected files.
- Permission denied: Ensure read permissions for input and write permissions for output directory.
- Module import errors: Verify Python 3.10+ and run from the project root directory.

## License

This project is licensed under the MIT License - see LICENSE for details.

## Contributing

Contributions are welcome. See CONTRIBUTING.md for guidelines.

Areas for Contribution:
- New IaC format parsers
- Additional cloud vendor support (GCP, Alibaba)
- Service mapping expansions
- Documentation improvements
- Test coverage enhancements

## Support

- Issues: https://github.com/vunvulear/Cloud.ServiceAggregator/issues
- Discussions: https://github.com/vunvulear/Cloud.ServiceAggregator/discussions
- Documentation: See /docs folder

## Roadmap

- [ ] GCP support
- [ ] Terraform state file analysis
- [ ] Cost estimation per cloud
- [ ] Policy compliance checking
- [ ] Web UI dashboard
- [ ] CI/CD integration examples

## Statistics

- Supported Formats: 12+ IaC formats
- Supported Languages: 8+ programming languages
- Services Mapped: 200+ Azure/AWS services
- Test Coverage: 170+ tests

---

Repository: https://github.com/vunvulear/Cloud.ServiceAggregator

Built for multi-cloud infrastructure management
