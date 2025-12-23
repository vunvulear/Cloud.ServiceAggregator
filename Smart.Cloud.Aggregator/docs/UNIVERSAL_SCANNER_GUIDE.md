# Universal Scanner Guide

The universal scanner discovers files by language and hands them to the appropriate parser.

Languages
- Terraform (.tf)
- Bicep (.bicep)
- PowerShell (.ps1)
- Azure CLI in Bash (.sh)
- ARM Templates (.json)
- CloudFormation (.json/.yaml/.yml)
- Python (.py) — AWS SDK detection
- Bash (.sh) — AWS CLI detection
- TypeScript (.ts/.tsx) — AWS CDK/SDK detection
- Go (.go) — AWS SDK detection
- Java/C# (.java/.cs) — AWS SDK detection

Configuration
- LanguageRegistry registers supported languages and points to vendor modules:
  - Azure module names: `azure.parsers.<name>`
  - AWS module names: `aws.parsers.<name>`
- DirectoryScanner:
  - scan_all(directory, verbose=False)
  - scan_single_language(directory, IaCLanguage, verbose=False)
  - add_excluded_directory(name)

Statistics
- Scanner returns a ScanResult containing:
  - total_iac_files
  - files_by_language
  - files_by_extension
  - supported_languages

Example
- from src.universal_scanner import create_scanner
- result = create_scanner().scan_all("./infra", verbose=True)
- stats = scanner.get_statistics(result)
