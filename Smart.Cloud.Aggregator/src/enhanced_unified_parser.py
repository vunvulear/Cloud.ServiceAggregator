#!/usr/bin/env python3
"""
Enhanced Unified Parser Module

Combines all parsers (Terraform, Bicep, PowerShell, Azure CLI, ARM) 
to scan and parse all IaC formats simultaneously.
"""

from pathlib import Path
from typing import Dict, List, Set, Optional
from collections import defaultdict

from .azure.parsers.terraform import TerraformParser
from .azure.parsers.bicep import BicepParser
from .azure.parsers.powershell import PowerShellParser
from .azure.parsers.azure_cli import AzureCliParser
from .azure.parsers.arm import ArmTemplateParser
from .aws.parsers.cloudformation import CloudFormationParser
from .aws.parsers.python import PythonAWSParser
from .aws.parsers.bash import BashAWSParser
from .aws.parsers.typescript import TypeScriptAWSParser
from .aws.parsers.go import GoAWSParser
from .aws.parsers.java import JavaAWSParser
from .service_mapping import SERVICE_MAPPING
from .universal_scanner import DirectoryScanner, IaCLanguage, ScanResult


class EnhancedUnifiedIaCParser:
    """Enhanced parser supporting Terraform, Bicep, PowerShell, Azure CLI, ARM, CloudFormation, Python AWS, and Bash AWS"""

    def __init__(self, scanner: Optional[DirectoryScanner] = None):
        """
        Initialize the enhanced unified parser
        
        Args:
            scanner: Optional universal scanner instance
        """
        self.terraform_parser = TerraformParser()
        self.bicep_parser = BicepParser()
        self.powershell_parser = PowerShellParser()
        self.azure_cli_parser = AzureCliParser()
        self.arm_parser = ArmTemplateParser()
        self.cf_parser = CloudFormationParser()
        self.python_aws_parser = PythonAWSParser()
        self.bash_aws_parser = BashAWSParser()
        self.ts_aws_parser = TypeScriptAWSParser()
        self.go_aws_parser = GoAWSParser()
        self.java_aws_parser = JavaAWSParser()
        self.scanner = scanner or DirectoryScanner()
        self.all_resources: Dict[str, List[str]] = defaultdict(list)
        self.all_resource_groups: Set[str] = set()
        self.scan_result: Optional[ScanResult] = None
        self.parsed_by_format: Dict[str, int] = {}

    def parse_directory(
        self,
        directory: str,
        verbose: bool = False
    ) -> Dict[str, Dict]:
        """
        Parse all IaC file formats in a directory.
        
        Supports: Terraform, Bicep, PowerShell, Azure CLI, ARM Templates
        
        Args:
            directory: Path to directory containing IaC files
            verbose: Enable verbose output
            
        Returns:
            Dictionary of aggregated Azure services
            
        Raises:
            FileNotFoundError: If no supported files found
        """
        dir_path = Path(directory)
        
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        # Scan directory for all supported IaC files
        self.scan_result = self.scanner.scan_all(directory, verbose=verbose)
        
        if self.scan_result.total_files == 0:
            raise FileNotFoundError(
                f"No supported IaC files found in {directory}"
            )

        if verbose:
            print(f"\nDetected formats: {', '.join(self.scan_result.supported_languages)}\n")

        # Parse Terraform files if found
        if self.scan_result.has_files('Terraform'):
            tf_files = self.scan_result.get_files_by_language('Terraform')
            if verbose:
                print(f"[Terraform] Parsing {len(tf_files)} file(s)...")
            try:
                tf_result = self.terraform_parser.parse_files(directory)
                self._merge_results(tf_result)
                self.parsed_by_format['Terraform'] = len(tf_files)
            except Exception as e:
                print(f"Warning: Error parsing Terraform files: {e}")

        # Parse CloudFormation files if found
        if self.scan_result.has_files('CloudFormation'):
            cf_files = self.scan_result.get_files_by_language('CloudFormation')
            if verbose:
                print(f"[CloudFormation] Parsing {len(cf_files)} file(s)...")
            try:
                cf_result = self.cf_parser.parse_files(directory)
                self._merge_results(cf_result)
                self.parsed_by_format['CloudFormation'] = len(cf_files)
            except Exception as e:
                print(f"Warning: Error parsing CloudFormation files: {e}")

        # Parse Python AWS files if found
        if self.scan_result.has_files('Python'):
            py_files = self.scan_result.get_files_by_language('Python')
            if verbose:
                print(f"[Python] Parsing {len(py_files)} file(s)...")
            try:
                py_result = self.python_aws_parser.parse_files(directory)
                self._merge_results(py_result)
                self.parsed_by_format['Python'] = len(py_files)
            except Exception as e:
                print(f"Warning: Error parsing Python files: {e}")

        # Parse Bash AWS files if found
        if self.scan_result.has_files('Bash'):
            sh_files = self.scan_result.get_files_by_language('Bash')
            if verbose:
                print(f"[Bash] Parsing {len(sh_files)} file(s)...")
            try:
                sh_result = self.bash_aws_parser.parse_files(directory)
                self._merge_results(sh_result)
                self.parsed_by_format['Bash'] = len(sh_files)
            except Exception as e:
                print(f"Warning: Error parsing Bash files: {e}")

        # Parse Bicep files if found
        if self.scan_result.has_files('Bicep'):
            bicep_files = self.scan_result.get_files_by_language('Bicep')
            if verbose:
                print(f"[Bicep] Parsing {len(bicep_files)} file(s)...")
            try:
                bicep_result = self.bicep_parser.parse_files(directory)
                self._merge_results(bicep_result)
                self.parsed_by_format['Bicep'] = len(bicep_files)
            except Exception as e:
                print(f"Warning: Error parsing Bicep files: {e}")

        # Parse PowerShell files if found
        if self.scan_result.has_files('PowerShell'):
            ps_files = self.scan_result.get_files_by_language('PowerShell')
            if verbose:
                print(f"[PowerShell] Parsing {len(ps_files)} file(s)...")
            try:
                ps_result = self.powershell_parser.parse_files(directory)
                self._merge_results(ps_result)
                self.parsed_by_format['PowerShell'] = len(ps_files)
            except Exception as e:
                print(f"Warning: Error parsing PowerShell files: {e}")

        # Parse Azure CLI files if found
        if self.scan_result.has_files('Azure CLI'):
            cli_files = self.scan_result.get_files_by_language('Azure CLI')
            if verbose:
                print(f"[Azure CLI] Parsing {len(cli_files)} file(s)...")
            try:
                cli_result = self.azure_cli_parser.parse_files(directory)
                self._merge_results(cli_result)
                self.parsed_by_format['Azure CLI'] = len(cli_files)
            except Exception as e:
                print(f"Warning: Error parsing Azure CLI files: {e}")

        # Parse ARM template files if found
        if self.scan_result.has_files('ARM Template'):
            arm_files = self.scan_result.get_files_by_language('ARM Template')
            if verbose:
                print(f"[ARM] Parsing {len(arm_files)} file(s)...")
            try:
                arm_result = self.arm_parser.parse_files(directory)
                self._merge_results(arm_result)
                self.parsed_by_format['ARM Template'] = len(arm_files)
            except Exception as e:
                print(f"Warning: Error parsing ARM template files: {e}")

        # Parse TypeScript files if found
        if self.scan_result.has_files('TypeScript'):
            ts_files = self.scan_result.get_files_by_language('TypeScript')
            if verbose:
                print(f"[TypeScript] Parsing {len(ts_files)} file(s)...")
            try:
                ts_result = self.ts_aws_parser.parse_files(directory)
                self._merge_results(ts_result)
                self.parsed_by_format['TypeScript'] = len(ts_files)
            except Exception as e:
                print(f"Warning: Error parsing TypeScript files: {e}")

        # Parse Go files if found
        if self.scan_result.has_files('Go'):
            go_files = self.scan_result.get_files_by_language('Go')
            if verbose:
                print(f"[Go] Parsing {len(go_files)} file(s)...")
            try:
                go_result = self.go_aws_parser.parse_files(directory)
                self._merge_results(go_result)
                self.parsed_by_format['Go'] = len(go_files)
            except Exception as e:
                print(f"Warning: Error parsing Go files: {e}")

        # Parse Java/C# files if found
        if self.scan_result.has_files('Java/C#'):
            java_files = self.scan_result.get_files_by_language('Java/C#')
            if verbose:
                print(f"[Java/C#] Parsing {len(java_files)} file(s)...")
            try:
                java_result = self.java_aws_parser.parse_files(directory)
                self._merge_results(java_result)
                self.parsed_by_format['Java/C#'] = len(java_files)
            except Exception as e:
                print(f"Warning: Error parsing Java/C# files: {e}")

        # Aggregate and return results
        return self._aggregate_all_services()

    def parse_single_language(
        self,
        directory: str,
        language: IaCLanguage,
        verbose: bool = False
    ) -> Dict[str, Dict]:
        """
        Parse files of a single language
        
        Args:
            directory: Directory to scan
            language: Language to parse
            verbose: Enable verbose output
            
        Returns:
            Dictionary of aggregated Azure services
            
        Raises:
            FileNotFoundError: If no files found for language
        """
        self.scan_result = self.scanner.scan_single_language(
            directory,
            language,
            verbose=verbose
        )
        
        if self.scan_result.total_files == 0:
            raise FileNotFoundError(
                f"No {language.value} files found in {directory}"
            )
        
        # Parse based on language
        if language == IaCLanguage.TERRAFORM:
            result = self.terraform_parser.parse_files(directory)
        elif language == IaCLanguage.BICEP:
            result = self.bicep_parser.parse_files(directory)
        elif language == IaCLanguage.POWERSHELL:
            result = self.powershell_parser.parse_files(directory)
        elif language == IaCLanguage.AZURE_CLI:
            result = self.azure_cli_parser.parse_files(directory)
        elif language == IaCLanguage.ARM_TEMPLATE:
            result = self.arm_parser.parse_files(directory)
        elif language == IaCLanguage.CLOUDFORMATION:
            result = self.cf_parser.parse_files(directory)
        elif language == IaCLanguage.PYTHON:
            result = self.python_aws_parser.parse_files(directory)
        elif language == IaCLanguage.BASH:
            result = self.bash_aws_parser.parse_files(directory)
        elif language == IaCLanguage.TYPESCRIPT:
            result = self.ts_aws_parser.parse_files(directory)
        elif language == IaCLanguage.GO:
            result = self.go_aws_parser.parse_files(directory)
        elif language == IaCLanguage.JAVA:
            result = self.java_aws_parser.parse_files(directory)
        else:
            raise NotImplementedError(f"Parser for {language.value} not yet implemented")
        
        self._merge_results(result)
        return self._aggregate_all_services()

    def _merge_results(self, new_services: Dict[str, Dict]) -> None:
        """
        Merge parsed services into combined results.
        
        Args:
            new_services: Services dictionary from a parser
        """
        for category, services in new_services.items():
            for service_name, service_info in services.items():
                resource_type = service_info['resource_type']
                instances = service_info['instances']
                self.all_resources[resource_type].extend(instances)

    def _aggregate_all_services(self) -> Dict[str, Dict]:
        """
        Aggregate all resources by service category.
        
        Returns:
            Dictionary organized by category and service type
        """
        from collections import defaultdict
        aggregated: Dict[str, Dict] = defaultdict(lambda: defaultdict(list))
        
        for resource_type, instances in self.all_resources.items():
            if resource_type in SERVICE_MAPPING:
                category, service_name = SERVICE_MAPPING[resource_type]
                
                if category not in aggregated:
                    aggregated[category] = {}
                
                if service_name not in aggregated[category]:
                    aggregated[category][service_name] = {
                        'resource_type': resource_type,
                        'count': 0,
                        'instances': []
                    }
                
                # Update count and instances
                aggregated[category][service_name]['instances'].extend(instances)
                aggregated[category][service_name]['count'] = len(
                    aggregated[category][service_name]['instances']
                )
        
        return dict(aggregated)

    def get_scan_result(self) -> Optional[ScanResult]:
        """
        Get the last scan result
        
        Returns:
            ScanResult or None if no scan performed
        """
        return self.scan_result

    def get_parsed_files(self) -> Dict[str, List[str]]:
        """
        Get list of files that were parsed by each parser.
        
        Returns:
            Dictionary with parser names and file lists
        """
        return {
            'terraform': self.terraform_parser.get_parsed_files(),
            'bicep': self.bicep_parser.get_parsed_files(),
            'powershell': self.powershell_parser.get_parsed_files(),
            'azure_cli': self.azure_cli_parser.get_parsed_files(),
            'arm_template': self.arm_parser.get_parsed_files(),
            'cloudformation': self.cf_parser.get_parsed_files(),
            'python': self.python_aws_parser.get_parsed_files(),
            'bash': self.bash_aws_parser.get_parsed_files(),
            'typescript': self.ts_aws_parser.get_parsed_files(),
            'go': self.go_aws_parser.get_parsed_files(),
            'java': self.java_aws_parser.get_parsed_files()
        }

    def get_resource_groups(self) -> Set[str]:
        """
        Get set of all resource groups found.
        
        Returns:
            Set of resource group names
        """
        all_rgs = set()
        all_rgs.update(self.terraform_parser.get_resource_groups())
        all_rgs.update(self.bicep_parser.get_resource_groups())
        all_rgs.update(self.powershell_parser.get_resource_groups())
        all_rgs.update(self.azure_cli_parser.get_resource_groups())
        return all_rgs

    def get_summary(self) -> Dict[str, any]:
        """
        Get summary statistics about parsed resources.
        
        Returns:
            Dictionary with statistics
        """
        total_resources = sum(len(instances) for instances in self.all_resources.values())
        
        summary = {
            'total_resources': total_resources,
            'total_resource_types': len(self.all_resources),
            'terraform_files': len(self.terraform_parser.get_parsed_files()),
            'bicep_files': len(self.bicep_parser.get_parsed_files()),
            'powershell_files': len(self.powershell_parser.get_parsed_files()),
            'azure_cli_files': len(self.azure_cli_parser.get_parsed_files()),
            'arm_template_files': len(self.arm_parser.get_parsed_files()),
            'resource_groups': len(self.get_resource_groups()),
            'parsed_by_format': self.parsed_by_format
        }
        
        # Add scanner statistics if available
        if self.scan_result:
            summary['scan_statistics'] = self.scanner.get_statistics(self.scan_result)
        
        return summary

    def get_languages_found(self) -> List[str]:
        """
        Get list of IaC languages found during last scan
        
        Returns:
            List of language names
        """
        if self.scan_result:
            return self.scan_result.supported_languages
        return []
