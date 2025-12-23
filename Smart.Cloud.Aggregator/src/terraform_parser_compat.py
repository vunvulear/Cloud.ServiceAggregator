"""
Compatibility Layer - Terraform Parser

This file maintains backward compatibility. Import from here
will redirect to the new modular structure.
"""

from .parsers.terraform import TerraformParser

__all__ = ['TerraformParser']
