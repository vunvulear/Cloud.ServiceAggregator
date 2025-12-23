#!/usr/bin/env python3
"""
Universal IaC Scanner Module

Provides comprehensive directory scanning for multiple Infrastructure as Code formats.
Designed for extensibility to support future languages (CloudFormation, ARM, Helm, etc.)

Supports:
  - Terraform (.tf files)
  - Bicep (.bicep files)
  - Ready for: CloudFormation, ARM Templates, Helm, etc.
"""

import os
import glob
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum


class IaCLanguage(Enum):
    """Supported Infrastructure as Code languages"""
    TERRAFORM = "terraform"
    BICEP = "bicep"
    POWERSHELL = "powershell"
    AZURE_CLI = "azure_cli"
    ARM_TEMPLATE = "arm_template"
    CLOUDFORMATION = "cloudformation"
    PYTHON = "python"
    BASH = "bash"
    HELM = "helm"
    TYPESCRIPT = "typescript"
    GO = "go"
    DOTNET = "dotnet"


@dataclass
class LanguageConfig:
    """Configuration for a specific IaC language"""
    name: str
    language: IaCLanguage
    file_extensions: List[str]
    description: str
    parser_module: Optional[str] = None
    enabled: bool = True
    recursive: bool = True
    exclude_patterns: List[str] = field(default_factory=list)
    
    def get_extensions_pattern(self) -> str:
        """Get glob pattern for file extensions"""
        if not self.file_extensions:
            return ""
        patterns = [f"*.{ext.lstrip('.')}" for ext in self.file_extensions]
        return f"({','.join(patterns)})"


class LanguageRegistry:
    """Registry for supported IaC languages"""
    
    def __init__(self):
        """Initialize language registry with supported languages"""
        self._languages: Dict[IaCLanguage, LanguageConfig] = {}
        self._register_default_languages()
    
    def _register_default_languages(self):
        """Register default supported languages"""
        # Terraform
        self.register(LanguageConfig(
            name="Terraform",
            language=IaCLanguage.TERRAFORM,
            file_extensions=[".tf"],
            description="HashiCorp Terraform",
            parser_module="azure.parsers.terraform",
            enabled=True
        ))
        
        # Bicep
        self.register(LanguageConfig(
            name="Bicep",
            language=IaCLanguage.BICEP,
            file_extensions=[".bicep"],
            description="Azure Bicep",
            parser_module="azure.parsers.bicep",
            enabled=True
        ))
        
        # PowerShell
        self.register(LanguageConfig(
            name="PowerShell",
            language=IaCLanguage.POWERSHELL,
            file_extensions=[".ps1"],
            description="PowerShell Scripts",
            parser_module="azure.parsers.powershell",
            enabled=True
        ))
        
        # Azure CLI
        self.register(LanguageConfig(
            name="Azure CLI",
            language=IaCLanguage.AZURE_CLI,
            file_extensions=[".sh"],
            description="Azure CLI Shell Scripts",
            parser_module="azure.parsers.azure_cli",
            enabled=True
        ))
        
        # ARM Templates
        self.register(LanguageConfig(
            name="ARM Template",
            language=IaCLanguage.ARM_TEMPLATE,
            file_extensions=[".json"],
            description="Azure Resource Manager Templates",
            parser_module="azure.parsers.arm",
            enabled=True
        ))
        
        # CloudFormation (enable)
        self.register(LanguageConfig(
            name="CloudFormation",
            language=IaCLanguage.CLOUDFORMATION,
            file_extensions=[".json", ".yaml", ".yml"],
            description="AWS CloudFormation",
            parser_module="aws.parsers.cloudformation",
            enabled=True
        ))
        
        # Python (AWS detection via boto3)
        self.register(LanguageConfig(
            name="Python",
            language=IaCLanguage.PYTHON,
            file_extensions=[".py"],
            description="Python scripts (boto3)",
            parser_module="aws.parsers.python",
            enabled=True
        ))
        
        # Bash (AWS detection via aws cli)
        self.register(LanguageConfig(
            name="Bash",
            language=IaCLanguage.BASH,
            file_extensions=[".sh"],
            description="Bash scripts (aws cli)",
            parser_module="aws.parsers.bash",
            enabled=True
        ))
        
        # TypeScript (AWS CDK/SDK)
        self.register(LanguageConfig(
            name="TypeScript",
            language=IaCLanguage.TYPESCRIPT,
            file_extensions=[".ts", ".tsx"],
            description="TypeScript (AWS CDK/SDK)",
            parser_module="aws.parsers.typescript",
            enabled=True
        ))
        
        # Go (AWS SDK)
        self.register(LanguageConfig(
            name="Go",
            language=IaCLanguage.GO,
            file_extensions=[".go"],
            description="Go (AWS SDK)",
            parser_module="aws.parsers.go",
            enabled=True
        ))
        
        # .NET (Java/C#)
        self.register(LanguageConfig(
            name="Java/C#",
            language=IaCLanguage.DOTNET,
            file_extensions=[".java", ".cs"],
            description="Java/C# (AWS SDK)",
            parser_module="aws.parsers.java",
            enabled=True
        ))
    
    def register(self, config: LanguageConfig):
        """
        Register a new language
        
        Args:
            config: Language configuration
        """
        self._languages[config.language] = config
    
    def get(self, language: IaCLanguage) -> Optional[LanguageConfig]:
        """
        Get language configuration
        
        Args:
            language: IaC language
            
        Returns:
            Language configuration or None if not found
        """
        return self._languages.get(language)
    
    def get_enabled_languages(self) -> List[LanguageConfig]:
        """
        Get all enabled languages
        
        Returns:
            List of enabled language configurations
        """
        return [config for config in self._languages.values() if config.enabled]
    
    def get_all_languages(self) -> List[LanguageConfig]:
        """
        Get all languages (enabled and disabled)
        
        Returns:
            List of all language configurations
        """
        return list(self._languages.values())
    
    def enable_language(self, language: IaCLanguage):
        """Enable a language"""
        if language in self._languages:
            self._languages[language].enabled = True
    
    def disable_language(self, language: IaCLanguage):
        """Disable a language"""
        if language in self._languages:
            self._languages[language].enabled = False


@dataclass
class ScanResult:
    """Result of scanning a directory"""
    directory: Path
    total_files: int = 0
    files_by_language: Dict[str, List[str]] = field(default_factory=dict)
    files_by_type: Dict[str, List[str]] = field(default_factory=dict)
    excluded_patterns: List[str] = field(default_factory=list)
    scan_time_ms: float = 0.0
    
    @property
    def total_iac_files(self) -> int:
        """Get total IaC files found"""
        return sum(len(files) for files in self.files_by_language.values())
    
    @property
    def supported_languages(self) -> List[str]:
        """Get list of languages found"""
        return list(self.files_by_language.keys())
    
    def get_files_by_language(self, language: str) -> List[str]:
        """Get files for a specific language"""
        return self.files_by_language.get(language, [])
    
    def has_files(self, language: str) -> bool:
        """Check if files exist for a language"""
        return language in self.files_by_language and len(self.files_by_language[language]) > 0


class DirectoryScanner:
    """Universal directory scanner for IaC files"""
    
    def __init__(self, language_registry: Optional[LanguageRegistry] = None):
        """
        Initialize scanner
        
        Args:
            language_registry: Registry of supported languages (uses default if None)
        """
        self.registry = language_registry or LanguageRegistry()
        self._excluded_dirs: Set[str] = {
            '.git', '.gitignore', '__pycache__', '.terraform', '.venv',
            'node_modules', '.vscode', '.idea', 'vendor', 'dist', 'build',
            '.env', '.cache'
        }
    
    def add_excluded_directory(self, directory: str):
        """
        Add directory to exclusion list
        
        Args:
            directory: Directory name to exclude
        """
        self._excluded_dirs.add(directory)
    
    def remove_excluded_directory(self, directory: str):
        """
        Remove directory from exclusion list
        
        Args:
            directory: Directory name to remove from exclusion
        """
        self._excluded_dirs.discard(directory)
    
    def scan(
        self,
        directory: str,
        languages: Optional[List[IaCLanguage]] = None,
        recursive: bool = True,
        verbose: bool = False
    ) -> ScanResult:
        """
        Scan directory for IaC files
        
        Args:
            directory: Directory path to scan
            languages: List of languages to scan for (None = all enabled)
            recursive: Whether to scan recursively
            verbose: Print detailed scan information
            
        Returns:
            ScanResult with found files organized by language
            
        Raises:
            FileNotFoundError: If directory doesn't exist
            PermissionError: If directory can't be accessed
        """
        dir_path = Path(directory)
        
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        if not dir_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory}")
        
        result = ScanResult(directory=dir_path)
        
        # Determine which languages to scan
        if languages:
            target_languages = [self.registry.get(lang) for lang in languages if self.registry.get(lang)]
        else:
            target_languages = self.registry.get_enabled_languages()
        
        if verbose:
            print(f"Scanning directory: {directory}")
            print(f"Languages: {', '.join(cfg.name for cfg in target_languages)}")
            print(f"Recursive: {recursive}")
            print()
        
        # Scan for each language
        for language_config in target_languages:
            if not language_config.enabled:
                continue
            
            files = self._scan_for_language(
                dir_path,
                language_config,
                recursive,
                verbose
            )
            
            if files:
                result.files_by_language[language_config.name] = files
                
                # Also organize by file type
                for file_path in files:
                    ext = Path(file_path).suffix
                    if ext not in result.files_by_type:
                        result.files_by_type[ext] = []
                    result.files_by_type[ext].append(file_path)
                
                if verbose:
                    print(f"  [{language_config.name}] Found {len(files)} file(s)")
        
        result.total_files = result.total_iac_files
        
        if verbose:
            print(f"\nTotal files found: {result.total_files}")
        
        return result
    
    def _scan_for_language(
        self,
        directory: Path,
        language_config: LanguageConfig,
        recursive: bool,
        verbose: bool
    ) -> List[str]:
        """
        Scan for files of a specific language
        
        Args:
            directory: Directory to scan
            language_config: Language configuration
            recursive: Scan recursively
            verbose: Print progress
            
        Returns:
            List of file paths found
        """
        files = []
        
        for ext in language_config.file_extensions:
            # Ensure extension starts with dot
            if not ext.startswith('.'):
                ext = f".{ext}"
            
            # Build glob pattern
            if recursive:
                pattern = f"**/*{ext}"
            else:
                pattern = f"*{ext}"
            
            # Search for files
            for file_path in directory.glob(pattern):
                # Skip excluded directories
                if self._should_exclude(file_path):
                    continue
                
                if file_path.is_file():
                    files.append(str(file_path))
        
        # Sort for consistency
        files.sort()
        return files
    
    def _should_exclude(self, file_path: Path) -> bool:
        """
        Check if file should be excluded
        
        Args:
            file_path: Path to check
            
        Returns:
            True if should be excluded, False otherwise
        """
        # Check if any part of the path is in excluded directories
        for part in file_path.parts:
            if part in self._excluded_dirs:
                return True
        return False
    
    def scan_all(self, directory: str, verbose: bool = False) -> ScanResult:
        """
        Scan all enabled languages in a directory
        
        Args:
            directory: Directory to scan
            verbose: Print progress
            
        Returns:
            ScanResult with all files found
        """
        return self.scan(directory, recursive=True, verbose=verbose)
    
    def scan_single_language(
        self,
        directory: str,
        language: IaCLanguage,
        verbose: bool = False
    ) -> ScanResult:
        """
        Scan for files of a single language
        
        Args:
            directory: Directory to scan
            language: Language to scan for
            verbose: Print progress
            
        Returns:
            ScanResult with files for specified language
        """
        return self.scan(directory, languages=[language], recursive=True, verbose=verbose)
    
    def get_statistics(self, result: ScanResult) -> Dict[str, any]:
        """
        Get statistics about scan results
        
        Args:
            result: Scan result
            
        Returns:
            Dictionary of statistics
        """
        stats = {
            'directory': str(result.directory),
            'total_files': result.total_files,
            'languages_found': result.supported_languages,
            'files_by_language': {
                lang: len(files)
                for lang, files in result.files_by_language.items()
            },
            'files_by_extension': {
                ext: len(files)
                for ext, files in result.files_by_type.items()
            }
        }
        return stats


class ScannerFactory:
    """Factory for creating scanners with specific configurations"""
    
    def __init__(self):
        """Initialize factory"""
        self._registry = LanguageRegistry()
    
    def create_default_scanner(self) -> DirectoryScanner:
        """
        Create scanner with default configuration
        
        Returns:
            Configured DirectoryScanner
        """
        return DirectoryScanner(self._registry)
    
    def create_custom_scanner(
        self,
        enabled_languages: Optional[List[IaCLanguage]] = None
    ) -> DirectoryScanner:
        """
        Create scanner with custom language configuration
        
        Args:
            enabled_languages: List of languages to enable
            
        Returns:
            Configured DirectoryScanner
        """
        registry = LanguageRegistry()
        
        if enabled_languages:
            # Disable all languages first
            for lang in registry.get_all_languages():
                registry.disable_language(lang.language)
            
            # Enable specified languages
            for lang in enabled_languages:
                registry.enable_language(lang)
        
        return DirectoryScanner(registry)
    
    def get_registry(self) -> LanguageRegistry:
        """Get language registry"""
        return self._registry


def create_scanner() -> DirectoryScanner:
    """
    Create a default scanner (convenience function)
    
    Returns:
        Configured DirectoryScanner ready for use
    """
    factory = ScannerFactory()
    return factory.create_default_scanner()


if __name__ == '__main__':
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python scanner.py <directory> [--verbose]")
        sys.exit(1)
    
    directory = sys.argv[1]
    verbose = '--verbose' in sys.argv
    
    scanner = create_scanner()
    result = scanner.scan_all(directory, verbose=verbose)
    
    print("\nScan Results:")
    print("=" * 60)
    
    stats = scanner.get_statistics(result)
    print(f"Directory: {stats['directory']}")
    print(f"Total IaC Files: {stats['total_files']}")
    print(f"Languages Found: {', '.join(stats['languages_found'])}")
    print()
    
    print("Files by Language:")
    for lang, count in stats['files_by_language'].items():
        print(f"  {lang}: {count}")
    
    print()
    print("Files by Extension:")
    for ext, count in stats['files_by_extension'].items():
        print(f"  {ext}: {count}")
