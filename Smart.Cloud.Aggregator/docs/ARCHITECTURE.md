# Smart Cloud Aggregator - Architecture

## Overview

Smart Cloud Aggregator is a multi-format Infrastructure as Code (IaC) analyzer that scans Terraform, Bicep, ARM, and several scripting languages to identify and report on Azure and AWS services used in your infrastructure.

---

## Architecture & Structure

```
Smart.Cloud.Aggregator/
?? src/
?  ?? azure/
?  ?  ?? parsers/
?  ?  ?  ?? terraform.py            # wraps Terraform Azure parser
?  ?  ?  ?? bicep.py                # wraps Bicep parser
?  ?  ?  ?? powershell.py           # wraps PowerShell parser
?  ?  ?  ?? azure_cli.py            # Azure CLI parser (implementation)
?  ?  ?  ?? arm.py                  # wraps ARM template parser
?  ?  ?? __init__.py
?  ?? aws/
?  ?  ?? parsers/
?  ?  ?  ?? cloudformation.py       # wraps CloudFormation parser
?  ?  ?  ?? python.py               # wraps Python AWS parser
?  ?  ?  ?? bash.py                 # wraps Bash AWS parser
?  ?  ?  ?? typescript.py           # wraps TypeScript AWS parser
?  ?  ?  ?? go.py                   # wraps Go AWS parser
?  ?  ?  ?? java.py                 # wraps Java/C# AWS parser
?  ?  ?? __init__.py
?  ?? parsers/                      # core implementations
?  ?  ?? terraform/terraform_parser.py
?  ?  ?? bicep/bicep_parser.py
?  ?  ?? powershell/powershell_parser.py
?  ?  ?? azure_cli/azure_cli_parser.py
?  ?  ?? arm/arm_template_parser.py
?  ?  ?? cloudformation/cloudformation_parser.py
?  ?  ?? python/python_aws_parser.py
?  ?  ?? bash/bash_aws_parser.py
?  ?  ?? typescript/typescript_aws_parser.py
?  ?  ?? go/go_aws_parser.py
?  ?  ?? java/java_aws_parser.py
?  ?? service_mapping.py            # Azure + AWS resource type ? category mapping
?  ?? universal_scanner.py          # language-aware file discovery
?  ?? unified_parser.py             # legacy unified (Azure-focused)
?  ?? enhanced_unified_parser.py    # multi-cloud unified parser
?  ?? report_generator.py
?  ?? __init__.py
?? docs/
?  ?? README.md
?  ?? QUICKSTART.md
?  ?? TESTING_GUIDE.md
?  ?? UNIVERSAL_SCANNER_GUIDE.md
?  ?? ARCHITECTURE.md
?  ?? SUPPORTED_SERVICES_BY_PARSER.md
?? scripts/
?  ?? generate_supported_services_by_parser.py
?? testing/
?  ?? test_*.py
?  ?? README.md
?? main.py                          # unified app entry point
?? README.md                        # project index
```

Core components
- Service Mapping: centralized mapping for Azure and AWS (expanded coverage)
- Base Parser: common parser interface
- Parsers: Terraform, Bicep, ARM, PowerShell, Azure CLI, CloudFormation, and language parsers (Python/TypeScript/Go/Java/C#) for AWS
- Vendor namespaces: `src/azure/parsers` and `src/aws/parsers` re-export vendor-specific parsers
- Universal Scanner: discovers files by language
- Unified Parsers: aggregate results across formats
- Report Generator: emits Markdown/JSON

Entry point
- Use `python main.py <dir>` (directory optional; defaults to current directory)
- For legacy-only Azure unified, `src/unified_parser.py` remains, but prefer `enhanced_unified_parser.py`

Outputs
- `azure_services_report.md` and optional JSON in working directory
- `docs/SUPPORTED_SERVICES_BY_PARSER.md` lists services by parser grouped by cloud vendor
