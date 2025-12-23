# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-23

### Added

#### Core Features
- Multi-cloud IaC analysis for Azure and AWS
- 12+ supported IaC formats (Terraform, Bicep, ARM Templates, CloudFormation, etc.)
- Universal language scanner for automatic file discovery
- Multi-format parser support (Terraform, Bicep, ARM, CloudFormation, etc.)
- Code-based IaC detection (Python, TypeScript, Go, Java/C#)

#### Report Generation
- Markdown reports with vendor-separated sections
- JSON reports with detailed resource metadata
- Services grouped by category and cloud vendor
- Resource summary statistics
- Languages detected during analysis

#### Functionality
- Recursive directory scanning
- Configurable output directory
- Verbose mode for debugging
- Metadata collection (resource groups, languages found)
- Service mapping for 200+ Azure and AWS resources

#### Documentation
- Comprehensive README with quick start
- Architecture overview document
- Universal Scanner guide
- Testing guide
- Supported services reference

#### Testing
- 170+ unit and integration tests
- Test coverage for all parsers
- Report generation validation
- Service mapping verification
- End-to-end workflow tests

### Features

#### CLI Interface
```bash
python main.py <directory> [options]
  -j, --json              Generate JSON report
  --json-only             Only JSON (skip markdown)
  -v, --verbose           Verbose output
  --scan-only             Scan only (no parsing)
  --language <lang>       Limit to specific language
  -o, --output <file>     Output file name
```

#### Report Structure

**Markdown Reports:**
- Cloud Services Assessment Report header
- Analysis metadata (files analyzed, languages found)
- Summary statistics
- Services by cloud vendor (Azure, AWS)
- Detailed resource list by vendor

**JSON Reports:**
- Timestamp (ISO 8601)
- Summary (categories, services, resources)
- Metadata (resource groups, languages)
- Services (all resources combined)
- Vendors (resources grouped by cloud)

#### Parsers
- TerraformParser - `.tf` files
- BicepParser - `.bicep` files
- ARMTemplateParser - ARM Templates
- CloudFormationParser - CloudFormation templates
- PowerShellParser - `.ps1` files
- AzureCliParser - `.sh` files with Azure CLI
- PythonParser - AWS SDK detection
- TypeScriptParser - AWS CDK/SDK detection
- GoParser - AWS SDK detection
- JavaParser/CSharpParser - AWS SDK detection

### Infrastructure
- No external runtime dependencies
- Pure Python implementation
- 3.10+ compatibility

---

## Planned Releases

### [1.1.0] - Q1 2025
- [ ] GCP support
- [ ] Terraform state file analysis
- [ ] Performance optimizations
- [ ] Enhanced error messages

### [1.2.0] - Q2 2025
- [ ] Web dashboard UI
- [ ] Cost estimation
- [ ] Policy compliance checking
- [ ] CI/CD integration examples

### [2.0.0] - Q3 2025
- [ ] Additional cloud providers (Alibaba, IBM)
- [ ] API endpoint
- [ ] Plugin system for custom parsers

---

## Legend

- **Added** - New features
- **Changed** - Changes in existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security vulnerability fixes

---

For migration guides, see the [MIGRATION.md](docs/MIGRATION.md) file.

For detailed commit history, see [GitHub Commits](https://github.com/vunvulear/Cloud.ServiceAggregator/commits/main).
