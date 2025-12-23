"""Azure parsers namespace."""

from .terraform import TerraformParser
from .bicep import BicepParser
from .powershell import PowerShellParser
from .azure_cli import AzureCliParser
from .arm import ArmTemplateParser

__all__ = [
    'TerraformParser',
    'BicepParser',
    'PowerShellParser',
    'AzureCliParser',
    'ArmTemplateParser',
]
