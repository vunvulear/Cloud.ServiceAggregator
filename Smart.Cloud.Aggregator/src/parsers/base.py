"""
Base Parser Module

Provides abstract base class for infrastructure as code parsers.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict


class BaseIaCParser(ABC):
    """Abstract base class for Infrastructure as Code parsers"""

    def __init__(self):
        """Initialize the parser"""
        self.resources: Dict[str, List[str]] = defaultdict(list)
        self.resource_groups: Set[str] = set()
        self.parsed_files: List[str] = []

    @abstractmethod
    def parse_files(self, directory: str) -> Dict[str, Dict]:
        """
        Parse all supported files in a directory.
        
        Args:
            directory: Path to directory containing IaC files
            
        Returns:
            Dictionary of aggregated Azure services
        """
        pass

    @abstractmethod
    def _extract_resources(self, content: str, file_path: Path) -> None:
        """
        Extract Azure resources from file content.
        
        Args:
            content: File content as string
            file_path: Path to the file being parsed
        """
        pass

    @abstractmethod
    def get_file_extensions(self) -> List[str]:
        """
        Get list of file extensions this parser handles.
        
        Returns:
            List of file extensions (e.g., ['.tf', '.bicep'])
        """
        pass

    def _aggregate_services(self) -> Dict[str, Dict]:
        """
        Aggregate resources by service category.
        
        Returns:
            Dictionary organized by category and service type
        """
        from ..service_mapping import SERVICE_MAPPING
        
        aggregated: Dict[str, Dict] = defaultdict(lambda: defaultdict(list))
        
        for resource_type, instances in self.resources.items():
            if resource_type in SERVICE_MAPPING:
                category, service_name = SERVICE_MAPPING[resource_type]
                
                aggregated[category][service_name] = {
                    'resource_type': resource_type,
                    'count': len(instances),
                    'instances': instances
                }
        
        return dict(aggregated)

    def get_parsed_files(self) -> List[str]:
        """
        Get list of files that were parsed.
        
        Returns:
            List of file paths
        """
        return self.parsed_files

    def get_resource_groups(self) -> Set[str]:
        """
        Get set of resource groups found.
        
        Returns:
            Set of resource group names
        """
        return self.resource_groups
