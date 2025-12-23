"""
Unified Parser Module

Combines Terraform and Bicep parsers to scan both file types.
Includes universal directory scanning with support for future languages.
"""

from pathlib import Path
from typing import Dict, List, Set, Optional
from collections import defaultdict

from .parsers.terraform import TerraformParser
from .parsers.bicep import BicepParser
from .parsers.powershell import PowerShellParser
from .parsers.azure_cli import AzureCliParser
from .parsers.arm import ArmTemplateParser
from .service_mapping import SERVICE_MAPPING
from .universal_scanner import DirectoryScanner, IaCLanguage, ScanResult


class UnifiedIaCParser:
    """Unified parser that handles all IaC formats (Terraform, Bicep, PowerShell, CLI, ARM)"""

    def __init__(self, scanner: Optional[DirectoryScanner] = None):
        """
        Initialize the UnifiedIaCParser.

        :param scanner: An optional DirectoryScanner instance for scanning directories.
        """
        self.scanner = scanner or DirectoryScanner()
        self.terraform_parser = TerraformParser()
        self.bicep_parser = BicepParser()
        self.powershell_parser = PowerShellParser()
        self.azure_cli_parser = AzureCliParser()
        self.arm_template_parser = ArmTemplateParser()
        self.scan_result = None
        self.debug_info = defaultdict(list)
        self._last_aggregated: Optional[Dict] = None

    def parse_directory(self, directory: Path, verbose: bool = False) -> Dict:
        """Parse the given directory for infrastructure as code files.

        :param directory: The directory to scan and parse.
        :param verbose: Enable verbose output.
        :return: A dictionary containing the parsed results.
        """
        if verbose:
            print(f"Scanning directory: {directory}")

        # Use scanner to get scan result
        self.scan_result = self.scanner.scan_all(str(directory), verbose=verbose)

        # Collect resources parsed
        all_resources = defaultdict(list)

        # Terraform
        if self.scan_result.has_files('Terraform'):
            files = self.scan_result.get_files_by_language('Terraform')
            if verbose:
                print(f"\nParsing {len(files)} Terraform file(s)...")
            try:
                result = self.terraform_parser.parse_files(str(directory))
                for category in result.values():
                    for svc in category.values():
                        all_resources[svc['resource_type']].extend(svc['instances'])
            except Exception as e:
                print(f"Warning: Error parsing Terraform files: {e}")

        # Bicep
        if self.scan_result.has_files('Bicep'):
            files = self.scan_result.get_files_by_language('Bicep')
            if verbose:
                print(f"\nParsing {len(files)} Bicep file(s)...")
            try:
                result = self.bicep_parser.parse_files(str(directory))
                for category in result.values():
                    for svc in category.values():
                        all_resources[svc['resource_type']].extend(svc['instances'])
            except Exception as e:
                print(f"Warning: Error parsing Bicep files: {e}")

        # Aggregate
        from collections import defaultdict as _dd
        from .service_mapping import resolve_service_category
        aggregated = _dd(dict)
        for rtype, instances in all_resources.items():
            resolved = resolve_service_category(rtype)
            if not resolved:
                continue
            category, sname = resolved
            if sname not in aggregated[category]:
                aggregated[category][sname] = {
                    'resource_type': rtype,
                    'count': 0,
                    'instances': []
                }
            aggregated[category][sname]['instances'].extend(instances)
            aggregated[category][sname]['count'] = len(aggregated[category][sname]['instances'])
        self._last_aggregated = dict(aggregated)
        return self._last_aggregated

    def _merge_results(self, new_result: Dict):
        """Merge new parsing results into the existing scan results."""
        for service, resources in new_result.items():
            self.scan_result.add_service_resources(service, resources)

    def _aggregate_all_services(self) -> Dict:
        """Aggregate and normalize all services' results into a single structure."""
        aggregated_results = {}
        for service, resources in self.scan_result.items():
            mapped_service = SERVICE_MAPPING.get(service, service)
            aggregated_results[mapped_service] = resources
        return aggregated_results

    def get_debug_info(self) -> Dict:
        """Get the debug information collected during parsing."""
        return dict(self.debug_info)

    def get_summary(self) -> Dict[str, any]:
        """Return summary stats for last parse."""
        if self.scan_result is None or self._last_aggregated is None:
            return {
                'total_resources': 0,
                'total_resource_types': 0,
                'terraform_files': 0,
                'bicep_files': 0,
                'resource_groups': 0,
            }
        total_resources = sum(
            svc['count'] for cat in self._last_aggregated.values() for svc in cat.values()
        )
        total_types = sum(1 for cat in self._last_aggregated.values() for _ in cat.values())
        tf_files = len(self.terraform_parser.get_parsed_files()) if hasattr(self.terraform_parser, 'get_parsed_files') else 0
        bicep_files = len(self.bicep_parser.get_parsed_files()) if hasattr(self.bicep_parser, 'get_parsed_files') else 0
        rg_count = len(getattr(self.terraform_parser, 'resource_groups', set()))
        return {
            'total_resources': total_resources,
            'total_resource_types': total_types,
            'terraform_files': tf_files,
            'bicep_files': bicep_files,
            'resource_groups': rg_count,
        }

    def get_parsed_files(self) -> Dict[str, List[str]]:
        """Return parsed files per parser for tests."""
        return {
            'terraform': self.terraform_parser.get_parsed_files(),
            'bicep': self.bicep_parser.get_parsed_files(),
            'powershell': self.powershell_parser.get_parsed_files(),
            'azure_cli': self.azure_cli_parser.get_parsed_files(),
            'arm_template': self.arm_template_parser.get_parsed_files(),
        }
