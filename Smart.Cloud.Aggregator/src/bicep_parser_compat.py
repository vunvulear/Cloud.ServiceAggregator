"""
Compatibility Layer - Bicep Parser

This file maintains backward compatibility. Import from here
will redirect to the new modular structure.
"""

from .parsers.bicep import BicepParser

__all__ = ['BicepParser']
