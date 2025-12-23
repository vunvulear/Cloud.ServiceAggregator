#!/usr/bin/env python3
"""
ARM Template Parser Module

Parses Azure Resource Manager (ARM) templates (.json).
Extracts Azure service information from ARM-based IaC.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any

from .base_parser import BaseIaCParser


class ArmTemplateParser(BaseIaCParser):
    """Parses ARM templates and extracts Azure resource information"""

    def __init__(self):
        """Initialize the ARM template parser"""
        super().__init__()

    def parse_files(self, arm_dir: str) -> Dict[str, Dict]:
        """
        Parse all ARM template files in a directory.
        
        Args:
            arm_dir: Path to directory containing ARM template files
            
        Returns:
            Dictionary of aggregated Azure services
            
        Raises:
            FileNotFoundError: If directory doesn't exist or no template files found
        """
        arm_path = Path(arm_dir)
        
        if not arm_path.exists():
            raise FileNotFoundError(f"ARM template directory not found: {arm_dir}")

        # Find all .json files that look like ARM templates
        json_files = list(arm_path.glob('**/*.json'))
        
        if not json_files:
            raise FileNotFoundError(f"No JSON files found in {arm_dir}")

        print(f"Found {len(json_files)} JSON file(s)")

        # Parse each file
        valid_count = 0
        for json_file in json_files:
            if self._is_arm_template(json_file):
                self._parse_file(json_file)
                valid_count += 1

        if valid_count == 0:
            raise FileNotFoundError(f"No ARM templates found in {arm_dir}")

        print(f"Parsed {valid_count} ARM template(s)")

        return self._aggregate_services()

    def _is_arm_template(self, file_path: Path) -> bool:
        """
        Check if a JSON file is an ARM template.
        
        ARM templates have schema property pointing to azuredeploy schema
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            True if file is an ARM template
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Check for ARM template indicators
            if '$schema' in data:
                schema = str(data.get('$schema', '')).lower()
                if 'schemas.microsoft.com' in schema or 'deploymenttemplate' in schema:
                    return True
            
            # Check for resources key (all ARM templates have this)
            if 'resources' in data and isinstance(data['resources'], list):
                return True
            
            return False
        except (json.JSONDecodeError, Exception):
            return False

    def _parse_file(self, file_path: Path) -> None:
        """
        Parse a single ARM template file.
        
        Args:
            file_path: Path to the ARM template JSON file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                template = json.load(f)
                self._extract_resources(template, file_path)
                self.parsed_files.append(str(file_path))
        except Exception as e:
            print(f"Warning: Error parsing {file_path}: {e}")

    def _extract_resources(self, template: Dict[str, Any], file_path: Path) -> None:
        """
        Extract Azure resources from ARM template.
        
        ARM template structure:
            {
              "$schema": "...",
              "contentVersion": "1.0.0.0",
              "resources": [
                {
                  "type": "Microsoft.Storage/storageAccounts",
                  "apiVersion": "2021-04-01",
                  "name": "mystorageaccount",
                  ...
                }
              ]
            }
        
        Args:
            template: Parsed ARM template dictionary
            file_path: Path to the file
        """
        if not isinstance(template, dict):
            return
        
        # Extract resources
        resources = template.get('resources', [])
        if not isinstance(resources, list):
            return
        
        for resource in resources:
            if not isinstance(resource, dict):
                continue
            
            resource_type = resource.get('type', '')
            
            # Check if it's a Microsoft resource
            if resource_type and resource_type.startswith('Microsoft.'):
                name = resource.get('name', 'unnamed')
                full_resource_id = f"{resource_type}#{name}"
                self.resources[resource_type].append(full_resource_id)
                
                # Extract resource group information if available
                self._extract_metadata(resource, template)

    def _extract_metadata(self, resource: Dict[str, Any], template: Dict[str, Any]) -> None:
        """
        Extract metadata from ARM template resource.
        
        Args:
            resource: Individual resource object
            template: Full template (for context)
        """
        # Try to extract location (often implies a resource group)
        location = resource.get('location', '')
        if location and not location.startswith('['):
            # Not a function reference
            pass
        
        # Try to extract tags that might indicate resource group
        tags = resource.get('tags', {})
        if isinstance(tags, dict):
            rg = tags.get('resourceGroup', '')
            if rg:
                self.resource_groups.add(rg)

    def get_file_extensions(self) -> List[str]:
        """
        Get list of file extensions this parser handles.
        
        Returns:
            List of supported file extensions
        """
        return ['.json']
