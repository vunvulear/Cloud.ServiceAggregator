"""
Compatibility Layer - ARM Template Parser

This file maintains backward compatibility. Import from here
will redirect to the new modular structure.
"""

from .parsers.arm import ArmTemplateParser

__all__ = ['ArmTemplateParser']
