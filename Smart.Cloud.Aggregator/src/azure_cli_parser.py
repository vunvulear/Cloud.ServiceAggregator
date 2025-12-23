#!/usr/bin/env python3
"""
Azure CLI (Bash) Parser Module

Parses Bash scripts (.sh) containing Azure CLI commands.
Extracts Azure service information from CLI-based IaC.
"""

import re
from pathlib import Path
from typing import Dict, List

from .base_parser import BaseIaCParser


class AzureCliParser(BaseIaCParser):
    """Parses Azure CLI Bash scripts and extracts Azure resource information"""

    def __init__(self):
        """Initialize the Azure CLI parser"""
        super().__init__()
        # Azure CLI command patterns
        self.resource_patterns = [
            r'az\s+(\w+)\s+(\w+)',  # az storage create, az sql server create
            r'az\s+(\w+)\s+(\w+)\s+create',  # Explicit create commands
        ]

    def parse_files(self, cli_dir: str) -> Dict[str, Dict]:
        """
        Parse all Azure CLI shell scripts in a directory.
        
        Args:
            cli_dir: Path to directory containing .sh files
            
        Returns:
            Dictionary of aggregated Azure services
            
        Raises:
            FileNotFoundError: If directory doesn't exist or no .sh files found
        """
        cli_path = Path(cli_dir)
        
        if not cli_path.exists():
            raise FileNotFoundError(f"Azure CLI directory not found: {cli_dir}")

        # Find all .sh files
        sh_files = list(cli_path.glob('**/*.sh'))
        
        if not sh_files:
            raise FileNotFoundError(f"No Azure CLI shell scripts found in {cli_dir}")

        print(f"Found {len(sh_files)} Azure CLI shell script(s)")

        # Parse each file
        for sh_file in sh_files:
            self._parse_file(sh_file)

        return self._aggregate_services()

    def _parse_file(self, file_path: Path) -> None:
        """
        Parse a single shell script.
        
        Args:
            file_path: Path to the .sh file
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
        Extract Azure resources from Azure CLI bash script.
        
        Handles patterns like:
            az storage account create -n "myaccount" -g "rg"
            az sql server create --name "myserver" --resource-group "rg"
            az keyvault create --name "myvault" --resource-group "rg"
        
        Args:
            content: Bash script content
            file_path: Path to the file
        """
        # Remove comments
        content_no_comments = self._remove_comments(content)
        
        # Extract resource groups
        self._extract_resource_groups(content_no_comments)
        
        # Extract az commands (service and operation)
        cmd_pattern = r'az\s+(\w+)(?:\s+(\w+))*\s+(?:create|update)'
        for match in re.finditer(cmd_pattern, content_no_comments):
            service = match.group(1).strip()
            sub_service = match.group(2)
            
            resource_type = self._map_cli_to_resource_type(service, sub_service)
            
            if resource_type:
                full_resource_id = f"{resource_type}#{service}"
                self.resources[resource_type].append(full_resource_id)

    def _remove_comments(self, content: str) -> str:
        """
        Remove comments from bash script.
        
        Handles:
        - Single-line comments: # comment
        
        Args:
            content: Original content
            
        Returns:
            Content with comments removed
        """
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip shebang
            if line.startswith('#!'):
                cleaned_lines.append(line)
                continue
            
            comment_pos = line.find('#')
            if comment_pos != -1:
                # Check if # is inside a string
                in_string = False
                quote_char = None
                for i, char in enumerate(line):
                    if char in ('"', "'") and (i == 0 or line[i-1] != '\\'):
                        if not in_string:
                            in_string = True
                            quote_char = char
                        elif char == quote_char:
                            in_string = False
                    
                    if i == comment_pos and not in_string:
                        line = line[:i]
                        break
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)

    def _extract_resource_groups(self, content: str) -> None:
        """
        Extract resource group names from Azure CLI script.
        
        Args:
            content: Azure CLI script content
        """
        # Patterns for resource group extraction
        patterns = [
            r'--resource-group\s+["\']?([^\s"\']+)["\']?',
            r'-g\s+["\']?([^\s"\']+)["\']?',
            r'az\s+group\s+create\s+.*?--name\s+["\']?([^\s"\']+)["\']?',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content):
                rg_name = match.group(1).strip()
                if rg_name and not rg_name.startswith('$'):
                    self.resource_groups.add(rg_name)

    def _map_cli_to_resource_type(self, service: str, sub_service: str = None) -> str:
        """
        Map Azure CLI service to resource type.
        
        Args:
            service: Service name (e.g., 'storage', 'sql')
            sub_service: Sub-service if available
            
        Returns:
            Full resource type or empty string if not recognized
        """
        # Mapping of CLI service names to resource types
        mapping = {
            'storage': 'Microsoft.Storage/storageAccounts',
            'sql': 'Microsoft.Sql/servers',
            'network': 'Microsoft.Network/virtualNetworks',
            'keyvault': 'Microsoft.KeyVault/vaults',
            'appservice': 'Microsoft.Web/serverfarms',
            'webapp': 'Microsoft.Web/sites',
            'cosmos': 'Microsoft.DocumentDB/databaseAccounts',
            'identity': 'Microsoft.ManagedIdentity/userAssignedIdentities',
            'vm': 'Microsoft.Compute/virtualMachines',
            'acr': 'Microsoft.ContainerRegistry/registries',
            'aks': 'Microsoft.ContainerService/managedClusters',
            'monitor': 'Microsoft.Insights/components',
            'log-analytics': 'Microsoft.OperationalInsights/workspaces',
            'nsg': 'Microsoft.Network/networkSecurityGroups',
            'vnet': 'Microsoft.Network/virtualNetworks',
            'functionapp': 'Microsoft.Web/sites',
        }
        
        service_lower = service.lower()
        
        # Direct lookup
        if service_lower in mapping:
            return mapping[service_lower]
        
        # Try partial matching
        for key, value in mapping.items():
            if key in service_lower or service_lower in key:
                return value
        
        return ""

    def get_file_extensions(self) -> List[str]:
        """
        Get list of file extensions this parser handles.
        
        Returns:
            List of supported file extensions
        """
        return ['.sh']
