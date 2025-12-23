#!/usr/bin/env python3
"""
Smart Cloud Aggregator

Multi-format Infrastructure as Code analyzer for Azure and AWS services.

Supports:
- Terraform (.tf files)
- Bicep (.bicep files)
- ARM Templates (.json)
- PowerShell (.ps1)
- Azure CLI (Bash .sh)
- CloudFormation (YAML/JSON)
- Python/TypeScript/Go/Java/C# cloud SDK usage

When run without parameters, scans the current directory recursively.
Generates markdown and optional JSON reports of detected services.
"""

import argparse
import sys
from pathlib import Path

from src.enhanced_unified_parser import EnhancedUnifiedIaCParser as UnifiedIaCParser
from src.report_generator import ReportGenerator
from src.universal_scanner import IaCLanguage, DirectoryScanner, create_scanner


def _map_language_to_enum(language_str: str) -> IaCLanguage:
    mapping = {
        'terraform': IaCLanguage.TERRAFORM,
        'bicep': IaCLanguage.BICEP,
        'powershell': IaCLanguage.POWERSHELL,
        'cli': IaCLanguage.AZURE_CLI,
        'arm': IaCLanguage.ARM_TEMPLATE,
        'cloudformation': IaCLanguage.CLOUDFORMATION,
        'python': IaCLanguage.PYTHON,
        'typescript': IaCLanguage.TYPESCRIPT,
        'go': IaCLanguage.GO,
        'dotnet': IaCLanguage.DOTNET,
        'bash': IaCLanguage.BASH,
    }
    return mapping.get(language_str, IaCLanguage.TERRAFORM)


def main():
    parser = argparse.ArgumentParser(
        description='Analyze IaC and code to aggregate cloud services',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Examples:\n  %(prog)s . -j\n  %(prog)s ./infra --language terraform -v\n  %(prog)s --scan-only'
    )

    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='Directory to scan (default: current directory)'
    )
    parser.add_argument('-o', '--output', default='cloud_services_report.md', help='Output markdown file')
    parser.add_argument('-j', '--json', action='store_true', help='Also output JSON report')
    parser.add_argument('--json-only', action='store_true', help='Only output JSON report')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--scan-only', action='store_true', help='Only scan, do not parse')
    parser.add_argument('--language', choices=['terraform','bicep','powershell','cli','arm','cloudformation','python','typescript','go','dotnet','bash'], help='Limit to one language')
    parser.add_argument('--recursive', action='store_true', default=True, help='Recursive scan (default)')
    parser.add_argument('--no-recursive', action='store_false', dest='recursive', help='Disable recursive scan')
    parser.add_argument('--csv', action='store_true', help='Also output CSV report')

    args = parser.parse_args()

    try:
        if args.verbose or args.scan_only:
            print(f"Scanning directory: {args.directory}")
            scanner = create_scanner()
            if args.language:
                lang = _map_language_to_enum(args.language)
                scan_result = scanner.scan_single_language(args.directory, lang, verbose=True)
                print(f"\nFound {scan_result.total_files} file(s)")
            else:
                scan_result = scanner.scan_all(args.directory, verbose=True)
                print(f"\nTotal files found: {scan_result.total_files}")
            stats = scanner.get_statistics(scan_result)
            print("\nScan Statistics:")
            for lang, count in stats['files_by_language'].items():
                print(f"  - {lang}: {count}")

        if args.scan_only:
            return 0

        if args.verbose:
            print("\nAnalyzing files...")
        iac_parser = UnifiedIaCParser()
        if args.language:
            lang = _map_language_to_enum(args.language)
            aggregated = iac_parser.parse_single_language(args.directory, lang, verbose=args.verbose)
        else:
            aggregated = iac_parser.parse_directory(args.directory, verbose=args.verbose)

        # Always prepare metadata
        metadata = {
            'parsed_files': iac_parser.get_parsed_files(),
            'resource_groups': list(getattr(iac_parser, 'get_resource_groups', lambda: [])()),
            'languages_found': getattr(iac_parser, 'get_languages_found', lambda: [])(),
            'analyzed_folder': str(Path(args.directory).resolve()),
        }

        # Ensure output directory inside analyzed path exists
        out_dir = Path(args.directory) / 'Smart.Cloud.Aggregator.Output'
        out_dir.mkdir(parents=True, exist_ok=True)
        base_name = Path(args.output).name
        md_path = out_dir / base_name
        json_path = out_dir / base_name.replace('.md', '.json')
        csv_path = out_dir / base_name.replace('.md', '.csv')

        # Use empty dict if no resources to still generate reports
        services_to_report = aggregated or {}
        report = ReportGenerator(services_to_report, metadata, include_parsed_files=False, include_legacy_header=False)
        if not args.json_only:
            report.save_to_file(str(md_path), format='markdown')
        if args.json or args.json_only:
            report.save_to_file(str(json_path), format='json')
        if args.csv:
            report.save_to_file(str(csv_path), format='csv')

        summary = iac_parser.get_summary()
        print("\n" + "="*60)
        print("ANALYSIS SUMMARY")
        print("="*60)
        if 'scan_statistics' in summary:
            for lang, count in summary['scan_statistics']['files_by_language'].items():
                print(f"{lang} Files:               {count}")
        print(f"Total Resources:       {summary['total_resources']}")
        print(f"Total Resource Types:  {summary['total_resource_types']}")
        print(f"Terraform Files:       {summary['terraform_files']}")
        print(f"Bicep Files:           {summary['bicep_files']}")
        print(f"Resource Groups:       {summary['resource_groups']}")
        print("="*60)

        if not args.verbose:
            print("\n? Analysis complete!")
            if not args.json_only:
                print(f"? Report saved to: {md_path}")
            if args.json or args.json_only:
                print(f"? JSON saved to: {json_path}")
        return 0

    except (FileNotFoundError, NotADirectoryError) as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
