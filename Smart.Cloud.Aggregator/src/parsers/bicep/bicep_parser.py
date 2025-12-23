"""
Bicep Parser Module

Parses Bicep files (.bicep) and extracts Azure resource information.
Supports comprehensive Bicep syntax including child resources, decorators, and complex properties.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict as _dd

from ..base import BaseIaCParser
from ...service_mapping import SERVICE_MAPPING, resolve_service_category


class BicepParser(BaseIaCParser):
    """Parses Bicep files and extracts Azure resource information"""

    def __init__(self):
        """Initialize the Bicep parser"""
        super().__init__()
        # Single pattern: resource <name> '<type>' or '<type>@<version>'
        self.resource_pattern = r"resource\s+(\w+)\s+['\"]([^'\"]+?)\s*(?:@[^'\"]+)?['\"]\s*=\s*\{"

    def parse_files(self, bicep_dir: str) -> Dict[str, Dict]:
        """
        Parse all Bicep files in a directory.
        
        Args:
            bicep_dir: Path to directory containing Bicep files
            
        Returns:
            Dictionary of aggregated Azure services
            
        Raises:
            FileNotFoundError: If directory doesn't exist or no .bicep files found
        """
        bicep_path = Path(bicep_dir)
        
        if not bicep_path.exists():
            raise FileNotFoundError(f"Bicep directory not found: {bicep_dir}")

        # Find all .bicep files
        bicep_files = list(bicep_path.glob('**/*.bicep'))
        
        if not bicep_files:
            raise FileNotFoundError(f"No Bicep files found in {bicep_dir}")

        print(f"Found {len(bicep_files)} Bicep file(s)")

        # Parse each file
        for bicep_file in bicep_files:
            self._parse_file(bicep_file)

        return self._aggregate_services()

    def _parse_file(self, file_path: Path) -> None:
        """
        Parse a single Bicep file.
        
        Args:
            file_path: Path to the .bicep file
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
        Extract Azure resources from Bicep configuration.
        
        Handles multiple Bicep resource syntax variations:
            resource <symbolicName> '<type>@<api-version>' = { ... }
            resource <symbolicName> '<type>' = { ... }
            resource <symbolicName> '<type>@<version>' = parent: parentRef { ... }
        
        Args:
            content: Bicep file content
            file_path: Path to the file (for reference)
        """
        # Remove comments to avoid false matches
        content_no_comments = self._remove_comments(content)
        
        # Try single pattern and normalize resource type without @version
        seen = set()
        matches = re.finditer(self.resource_pattern, content_no_comments, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            symbolic_name = match.group(1).strip()
            rtype = match.group(2).strip()
            # Remove any @version suffix if present (defensive)
            if '@' in rtype:
                rtype = rtype.split('@', 1)[0]
            if not rtype.startswith('Microsoft.'):
                continue
            key = (rtype, symbolic_name)
            if key in seen:
                continue
            seen.add(key)
            full_resource_id = f"{rtype}#{symbolic_name}"
            self.resources[rtype].append(full_resource_id)
            # Extract resource group
            resource_section = self._extract_resource_section(content_no_comments, match.start())
            rg = self._extract_resource_group(resource_section)
            if rg:
                self.resource_groups.add(rg)

    def _remove_comments(self, content: str) -> str:
        """
        Remove comments from Bicep content to avoid false matches.
        
        Handles:
        - Single-line comments: // comment
        - Multi-line comments: /* comment */
        
        Args:
            content: Original content
            
        Returns:
            Content with comments removed
        """
        # Remove multi-line comments /* ... */
        content = re.sub(r'/\*[\s\S]*?\*/', '', content)
        
        # Remove single-line comments //
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            # Remove comments but keep string content
            comment_pos = line.find('//')
            if comment_pos != -1:
                # Check if // is inside a string
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
        
        In Bicep, resource group can be specified in various ways:
        - name: 'myResourceGroup'
        - resourceGroupName: 'myRG'
        - parent: reference
        - Via output reference
        
        Args:
            resource_section: The resource configuration section
            
        Returns:
            Resource group name or empty string
        """
        # Look for common resource group references
        patterns = [
            r"name:\s*['\"]([^'\"]+)['\"]",                      # name: 'myRG'
            r"resourceGroupName:\s*['\"]([^'\"]+)['\"]",         # resourceGroupName: 'myRG'
            r"resourceGroup\(\)['\"]([^'\"]+)['\"]",             # resourceGroup()['name']
            r"subscriptionResourceId\([^,]+,\s*['\"]([^'\"]+)", # subscriptionResourceId(..., 'myRG')
        ]
        
        for pattern in patterns:
            rg_match = re.search(pattern, resource_section, re.IGNORECASE)
            if rg_match:
                return rg_match.group(1).strip()
        
        return ""

    def get_file_extensions(self) -> List[str]:
        """
        Get list of file extensions this parser handles.
        
        Returns:
            List of supported file extensions
        """
        return ['.bicep']

    def get_resource_type_count(self) -> int:
        """
        Get count of unique resource types found.
        
        Returns:
            Number of unique resource types
        """
        return len(self.resources)

    def get_total_resource_count(self) -> int:
        """
        Get total count of resources found.
        
        Returns:
            Total number of resources
        """
        return sum(len(instances) for instances in self.resources.values())

    def _aggregate_services(self) -> Dict[str, Dict]:
        aggregated: Dict[str, Dict] = _dd(dict)
        for resource_type, instances in self.resources.items():
            resolved = resolve_service_category(resource_type)
            if not resolved:
                continue
            category, service_name = resolved
            aggregated.setdefault(category, {})[service_name] = {
                'resource_type': resource_type,
                'count': len(instances),
                'instances': instances,
            }
        return dict(aggregated)
