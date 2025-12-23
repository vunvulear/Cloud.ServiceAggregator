"""
Compatibility Layer - PowerShell Parser

This file maintains backward compatibility. Import from here
will redirect to the new modular structure.
"""

from .parsers.powershell import PowerShellParser

__all__ = ['PowerShellParser']
