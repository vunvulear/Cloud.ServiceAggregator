"""
Compatibility Layer - Base Parser

This file maintains backward compatibility. Import from here
will redirect to the new modular structure.
"""

from .parsers.base import BaseIaCParser

__all__ = ['BaseIaCParser']
