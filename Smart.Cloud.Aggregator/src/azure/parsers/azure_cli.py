#!/usr/bin/env python3
"""
Azure CLI (Bash) Parser Module

Parses Bash scripts (.sh) containing Azure CLI commands.
Extracts Azure service information from CLI-based IaC.
"""

import re
from pathlib import Path
from typing import Dict, List

from ...parsers.base import BaseIaCParser


class AzureCliParser(BaseIaCParser):
    def __init__(self):
        super().__init__()

    def parse_files(self, cli_dir: str) -> Dict[str, Dict]:
        cli_path = Path(cli_dir)
        if not cli_path.exists():
            raise FileNotFoundError(f"Azure CLI directory not found: {cli_dir}")
        sh_files = list(cli_path.glob('**/*.sh'))
        if not sh_files:
            raise FileNotFoundError(f"No Azure CLI shell scripts found in {cli_dir}")
        print(f"Found {len(sh_files)} Azure CLI shell script(s)")
        for sh_file in sh_files:
            self._parse_file(sh_file)
        return self._aggregate_services()

    def _parse_file(self, file_path: Path) -> None:
        try:
            content = file_path.read_text(encoding='utf-8')
            self._extract_resources(content, file_path)
            self.parsed_files.append(str(file_path))
        except Exception as e:
            print(f"Warning: Error parsing {file_path}: {e}")

    def _extract_resources(self, content: str, file_path: Path) -> None:
        content_no_comments = self._remove_comments(content)
        self._extract_resource_groups(content_no_comments)
        cmd_pattern = r'az\s+(\w+)(?:\s+(\w+))*\s+(?:create|update)'
        for match in re.finditer(cmd_pattern, content_no_comments):
            service = match.group(1).strip()
            sub_service = match.group(2)
            resource_type = self._map_cli_to_resource_type(service, sub_service)
            if resource_type:
                full_resource_id = f"{resource_type}#{service}"
                self.resources[resource_type].append(full_resource_id)

    def _remove_comments(self, content: str) -> str:
        lines = content.split('\n')
        cleaned = []
        for line in lines:
            if line.startswith('#!'):
                cleaned.append(line)
                continue
            comment_pos = line.find('#')
            if comment_pos != -1:
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
            cleaned.append(line)
        return '\n'.join(cleaned)

    def _extract_resource_groups(self, content: str) -> None:
        patterns = [
            r'--resource-group\s+["\']?([^\s"\']+)["\']?',
            r'-g\s+["\']?([^\s"\']+)["\']?',
            r'az\s+group\s+create\s+.*?--name\s+["\']?([^\s"\']+)["\']?',
        ]
        for pattern in patterns:
            for match in re.finditer(pattern, content):
                rg_name = match.group(1).strip()
                if rg_name and not rg_name.startswith('$'):
                    self.resource_groups.add(rg_name)

    def _map_cli_to_resource_type(self, service: str, sub_service: str = None) -> str:
        mapping = {
            'storage': 'Microsoft.Storage/storageAccounts',
            'sql': 'Microsoft.Sql/servers',
            'sqlmi': 'Microsoft.Sql/managedInstances',
            'network': 'Microsoft.Network/virtualNetworks',
            'dns': 'Microsoft.Network/dnsZones',
            'firewall': 'Microsoft.Network/azureFirewalls',
            'nat': 'Microsoft.Network/natGateways',
            'bastion': 'Microsoft.Network/bastionHosts',
            'keyvault': 'Microsoft.KeyVault/vaults',
            'appservice': 'Microsoft.Web/serverfarms',
            'webapp': 'Microsoft.Web/sites',
            'staticwebapp': 'Microsoft.Web/staticSites',
            'cosmos': 'Microsoft.DocumentDB/databaseAccounts',
            'identity': 'Microsoft.ManagedIdentity/userAssignedIdentities',
            'vm': 'Microsoft.Compute/virtualMachines',
            'vmss': 'Microsoft.Compute/virtualMachineScaleSets',
            'acr': 'Microsoft.ContainerRegistry/registries',
            'aks': 'Microsoft.ContainerService/managedClusters',
            'aks-fleet': 'Microsoft.ContainerService/fleets',
            'aro': 'Microsoft.RedHatOpenShift/openshiftClusters',
            'aca': 'Microsoft.App/containerApps',
            'containerapp': 'Microsoft.App/containerApps',
            'appconfig': 'Microsoft.AppConfiguration/configurationStores',
            'monitor': 'Microsoft.Insights/components',
            'log-analytics': 'Microsoft.OperationalInsights/workspaces',
            'nsg': 'Microsoft.Network/networkSecurityGroups',
            'vnet': 'Microsoft.Network/virtualNetworks',
            'functionapp': 'Microsoft.Web/sites',
            'databricks': 'Microsoft.Databricks/workspaces',
            'eventgrid': 'Microsoft.EventGrid/topics',
            'mediaservices': 'Microsoft.Media/mediaservices',
            'communication': 'Microsoft.Communication/communicationServices',
            'migrate': 'Microsoft.Migrate/migrateProjects',
            'recoveryservices': 'Microsoft.RecoveryServices/vaults',
            'eventhubs': 'Microsoft.EventHub/namespaces',
            'servicebus': 'Microsoft.ServiceBus/namespaces',
            'apim': 'Microsoft.ApiManagement/service',
            'signalr': 'Microsoft.SignalRService/signalR',
            'webpubsub': 'Microsoft.SignalRService/webPubSub',
            'dnszone': 'Microsoft.Network/dnsZones',
        }
        s = service.lower()
        if s in mapping:
            return mapping[s]
        for key, value in mapping.items():
            if key in s or s in key:
                return value
        return ""

    def get_file_extensions(self) -> List[str]:
        return ['.sh']

__all__ = ["AzureCliParser"]
