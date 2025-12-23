"""
Terraform Parser Module

Parses Terraform files (.tf) and extracts Azure/AWS resource information.
"""

import re
from pathlib import Path
from typing import Dict, List

from .base_parser import BaseIaCParser
from .service_mapping import SERVICE_MAPPING


class TerraformParser(BaseIaCParser):
    """Parses Terraform files and extracts Azure/AWS resource information"""

    def parse_files(self, terraform_dir: str) -> Dict[str, Dict]:
        """
        Parse all Terraform files in a directory.
        
        Args:
            terraform_dir: Path to directory containing Terraform files
            
        Returns:
            Dictionary of aggregated Azure/AWS services
            
        Raises:
            FileNotFoundError: If directory doesn't exist or no .tf files found
        """
        terraform_path = Path(terraform_dir)
        
        if not terraform_path.exists():
            raise FileNotFoundError(f"Terraform directory not found: {terraform_dir}")

        # Find all .tf files
        tf_files = list(terraform_path.glob('**/*.tf'))
        
        if not tf_files:
            raise FileNotFoundError(f"No Terraform files found in {terraform_dir}")

        print(f"Found {len(tf_files)} Terraform file(s)")

        # Parse each file
        for tf_file in tf_files:
            self._parse_file(tf_file)

        return self._aggregate_services()

    def _parse_file(self, file_path: Path) -> None:
        """
        Parse a single Terraform file.
        
        Args:
            file_path: Path to the .tf file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self._extract_resources(content, file_path)
                self.parsed_files.append(str(file_path))
        except Exception as e:
            print(f"Warning: Error parsing {file_path}: {e}")

    def _extract_resources(self, content: str, file_path: Path) -> None:
        """
        Extract Azure/AWS resources from Terraform configuration.
        
        Args:
            content: Terraform file content
            file_path: Path to the file (for reference)
        """
        # Pattern to match resource blocks: resource "type" "name"
        resource_pattern = r'resource\s+"([^"]+)"\s+"([^"]+)"\s*\{'
        
        for match in re.finditer(resource_pattern, content):
            resource_type = match.group(1)
            resource_name = match.group(2)

            # Accept both Azure (azurerm_*) and AWS (aws_*) resource types
            if resource_type.startswith('azurerm_') or resource_type.startswith('aws_'):
                full_resource_id = f"{resource_type}.{resource_name}"
                self.resources[resource_type].append(full_resource_id)

                # Azure RG extraction (AWS doesn’t use RG)
                if resource_type.startswith('azurerm_'):
                    section = self._extract_resource_section(content, match.start())
                    rg = self._extract_resource_group(section)
                    if rg:
                        self.resource_groups.add(rg)

    def _extract_resource_section(self, content: str, start_pos: int) -> str:
        """
        Extract the resource configuration section.
        
        Args:
            content: File content
            start_pos: Starting position in content
            
        Returns:
            The resource configuration section
        """
        brace_count = 0
        in_section = False
        section_start = start_pos
        
        for i in range(start_pos, len(content)):
            if content[i] == '{':
                if not in_section:
                    in_section = True
                    section_start = i
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
                if in_section and brace_count == 0:
                    return content[section_start:i+1]
        
        return ""

    def _extract_resource_group(self, resource_section: str) -> str:
        """
        Extract resource group name from resource configuration.
        
        Args:
            resource_section: The resource configuration section
            
        Returns:
            Resource group name or empty string
        """
        rg_match = re.search(
            r'resource_group_name\s*=\s*["\']?([^"\'\n}]+)["\']?',
            resource_section
        )
        if rg_match:
            return rg_match.group(1).strip().strip('"').strip("'")
        return ""

    def get_file_extensions(self) -> List[str]:
        """
        Get list of file extensions this parser handles.
        
        Returns:
            List of supported file extensions
        """
        return ['.tf']
