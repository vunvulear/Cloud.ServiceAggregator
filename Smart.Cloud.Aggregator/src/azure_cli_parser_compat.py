"""
Compatibility Layer - Azure CLI Parser

This file maintains backward compatibility. Import from here
will redirect to the new modular structure.
"""

from .parsers.azure_cli import AzureCliParser

__all__ = ['AzureCliParser']
