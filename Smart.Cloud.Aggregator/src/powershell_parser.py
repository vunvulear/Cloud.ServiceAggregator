#!/usr/bin/env python3
"""
PowerShell Parser Module

Parses PowerShell scripts (.ps1) for Azure resource definitions.
Extracts Azure service information from PowerShell-based IaC.
"""

import re
from pathlib import Path
from typing import Dict, List

from .base_parser import BaseIaCParser


class PowerShellParser(BaseIaCParser):
    """Parses PowerShell files and extracts Azure resource information"""

    def __init__(self):
        """Initialize the PowerShell parser"""
        super().__init__()
        # Common PowerShell cmdlet patterns for Azure resources
        self.resource_patterns = [
            # New-AzResource pattern
            r'New-AzResource\s+.*?-ResourceType\s+["\']?([^"\';\s]+)',
            # New-Az* cmdlets (New-AzStorageAccount, etc.)
            r'(New-Az\w+)',
            # Set-Az* cmdlets
            r'(Set-Az\w+)',
            # Get-Az* cmdlets
            r'(Get-Az\w+)',
        ]

    def parse_files(self, ps_dir: str) -> Dict[str, Dict]:
        """
        Parse all PowerShell files in a directory.
        
        Args:
            ps_dir: Path to directory containing PowerShell files
            
        Returns:
            Dictionary of aggregated Azure services
            
        Raises:
            FileNotFoundError: If directory doesn't exist or no .ps1 files found
        """
        ps_path = Path(ps_dir)
        
        if not ps_path.exists():
            raise FileNotFoundError(f"PowerShell directory not found: {ps_dir}")

        # Find all .ps1 files
        ps_files = list(ps_path.glob('**/*.ps1'))
        
        if not ps_files:
            raise FileNotFoundError(f"No PowerShell files found in {ps_dir}")

        print(f"Found {len(ps_files)} PowerShell file(s)")

        # Parse each file
        for ps_file in ps_files:
            self._parse_file(ps_file)

        return self._aggregate_services()

    def _parse_file(self, file_path: Path) -> None:
        """
        Parse a single PowerShell file.
        
        Args:
            file_path: Path to the .ps1 file
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
        Extract Azure resources from PowerShell script.
        
        Handles patterns like:
            New-AzStorageAccount -ResourceGroupName "rg" -Name "storage"
            New-AzResource -ResourceType "Microsoft.Storage/storageAccounts@2021-04-01"
            New-AzSqlServer -ResourceGroupName "rg" -ServerName "server"
        
        Args:
            content: PowerShell script content
            file_path: Path to the file
        """
        # Remove comments
        content_no_comments = self._remove_comments(content)
        
        # Extract resource groups
        self._extract_resource_groups(content_no_comments)
        
        # Extract New-Az* cmdlets (most common pattern)
        cmdlet_pattern = r'New-Az(\w+)'
        for match in re.finditer(cmdlet_pattern, content_no_comments):
            cmdlet_name = match.group(1)
            resource_type = self._map_cmdlet_to_resource_type(cmdlet_name)
            
            if resource_type:
                full_resource_id = f"{resource_type}#{cmdlet_name}"
                self.resources[resource_type].append(full_resource_id)

    def _remove_comments(self, content: str) -> str:
        """
        Remove comments from PowerShell content.
        
        Handles:
        - Single-line comments: # comment
        - Multi-line comments: <# comment #>
        
        Args:
            content: Original content
            
        Returns:
            Content with comments removed
        """
        # Remove multi-line comments <# ... #>
        content = re.sub(r'<#[\s\S]*?#>', '', content)
        
        # Remove single-line comments #
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            comment_pos = line.find('#')
            if comment_pos != -1:
                # Check if # is inside a string
                in_string = False
                quote_char = None
                for i, char in enumerate(line):
                    if char in ('"', "'") and (i == 0 or line[i-1] != '`'):
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
        Extract resource group names from PowerShell script.
        
        Args:
            content: PowerShell script content
        """
        # Pattern: -ResourceGroupName "name" or -ResourceGroupName 'name'
        patterns = [
            r"-ResourceGroupName\s+['\"]([^'\"]+)['\"]",
            r"-ResourceGroup\s+['\"]([^'\"]+)['\"]",
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content):
                rg_name = match.group(1).strip()
                if rg_name and not rg_name.startswith('$'):
                    self.resource_groups.add(rg_name)

    def _map_cmdlet_to_resource_type(self, cmdlet_name: str) -> str:
        """
        Map PowerShell cmdlet name to Azure resource type.
        
        Args:
            cmdlet_name: The cmdlet name (e.g., 'StorageAccount')
            
        Returns:
            Full resource type or empty string if not recognized
        """
        # Mapping of cmdlet patterns to resource types
        mapping = {
            'StorageAccount': 'Microsoft.Storage/storageAccounts',
            'SqlServer': 'Microsoft.Sql/servers',
            'SqlDatabase': 'Microsoft.Sql/servers/databases',
            'VirtualNetwork': 'Microsoft.Network/virtualNetworks',
            'NetworkSecurityGroup': 'Microsoft.Network/networkSecurityGroups',
            'PublicIPAddress': 'Microsoft.Network/publicIPAddresses',
            'KeyVault': 'Microsoft.KeyVault/vaults',
            'AppServicePlan': 'Microsoft.Web/serverfarms',
            'WebApp': 'Microsoft.Web/sites',
            'CosmosDBAccount': 'Microsoft.DocumentDB/databaseAccounts',
            'ManagedIdentity': 'Microsoft.ManagedIdentity/userAssignedIdentities',
            'VirtualMachine': 'Microsoft.Compute/virtualMachines',
            'ContainerRegistry': 'Microsoft.ContainerRegistry/registries',
            'KubernetesCluster': 'Microsoft.ContainerService/managedClusters',
            'ApplicationInsights': 'Microsoft.Insights/components',
            'LogAnalyticsWorkspace': 'Microsoft.OperationalInsights/workspaces',
        }
        
        # Direct lookup
        if cmdlet_name in mapping:
            return mapping[cmdlet_name]
        
        # Try partial matching
        for key, value in mapping.items():
            if key.lower() in cmdlet_name.lower():
                return value
        
        return ""

    def get_file_extensions(self) -> List[str]:
        """
        Get list of file extensions this parser handles.
        
        Returns:
            List of supported file extensions
        """
        return ['.ps1']
