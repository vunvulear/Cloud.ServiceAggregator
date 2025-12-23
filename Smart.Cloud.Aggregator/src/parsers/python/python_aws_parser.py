"""
Python AWS/Azure Parser

Parses Python scripts to detect AWS SDK (boto3) and Azure SDK (azure.*) resource usage.
"""

import re
from pathlib import Path
from typing import Dict, List

from ..base import BaseIaCParser

class PythonAWSParser(BaseIaCParser):
    """Parses Python files to detect AWS (boto3) and Azure (azure SDK) services"""

    def parse_files(self, directory: str) -> Dict[str, Dict]:
        p = Path(directory)
        if not p.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        files = list(p.glob('**/*.py'))
        if not files:
            raise FileNotFoundError(f"No Python files found in {directory}")
        print(f"Found {len(files)} Python file(s)")
        for f in files:
            self._parse_file(f)
        return self._aggregate_services()

    def _parse_file(self, file_path: Path) -> None:
        try:
            content = file_path.read_text(encoding='utf-8')
            self._extract_resources(content)
            self.parsed_files.append(str(file_path))
        except Exception as e:
            print(f"Warning: Error parsing {file_path}: {e}")

    def _extract_resources(self, content: str) -> None:
        # AWS boto3 patterns
        aws_patterns = {
            'aws_s3_bucket': r"boto3\.(client|resource)\(['\"]s3['\"]\)",
            'aws_lambda_function': r"boto3\.(client|resource)\(['\"]lambda['\"]\)",
            'aws_ec2_instance': r"boto3\.(client|resource)\(['\"]ec2['\"]\)",
            'aws_dynamodb_table': r"boto3\.(client|resource)\(['\"]dynamodb['\"]\)",
            'aws_rds_instance': r"boto3\.(client|resource)\(['\"]rds['\"]\)",
            'aws_kinesis_stream': r"boto3\.(client|resource)\(['\"]kinesis['\"]\)",
            'aws_glue_job': r"boto3\.(client|resource)\(['\"]glue['\"]\)",
            'aws_emr_cluster': r"boto3\.(client|resource)\(['\"]emr['\"]\)",
            'aws_opensearch_domain': r"boto3\.(client|resource)\(['\"]opensearch['\"]\)",
            'aws_redshift_cluster': r"boto3\.(client|resource)\(['\"]redshift['\"]\)",
            'aws_sns_topic': r"boto3\.(client|resource)\(['\"]sns['\"]\)",
            'aws_sqs_queue': r"boto3\.(client|resource)\(['\"]sqs['\"]\)",
            'aws_events_rule': r"boto3\.(client|resource)\(['\"]events['\"]\)",
            'aws_cloudwatch_log_group': r"boto3\.(client|resource)\(['\"]logs['\"]\)",
            'aws_eks_cluster': r"boto3\.(client|resource)\(['\"]eks['\"]\)",
            'aws_ecs_cluster': r"boto3\.(client|resource)\(['\"]ecs['\"]\)",
        }
        for key, pat in aws_patterns.items():
            if re.search(pat, content):
                self.resources[key].append(key)

        # Azure SDK patterns -> map to ARM provider types present in service_mapping
        azure_patterns = {
            'Microsoft.Storage/storageAccounts': r"\bazure\.storage\.blob\b",
            'Microsoft.Compute/virtualMachines': r"\bazure\.mgmt\.compute\b",
            'Microsoft.Network/virtualNetworks': r"\bazure\.mgmt\.network\b",
            'Microsoft.Sql/servers': r"\bazure\.mgmt\.sql\b",
            'Microsoft.Web/sites': r"\bazure\.mgmt\.web\b",
            'Microsoft.ContainerInstance/containerGroups': r"\bazure\.mgmt\.containerinstance\b",
            'Microsoft.ContainerService/managedClusters': r"\bazure\.mgmt\.containerservice\b",
            'Microsoft.Resources/resourceGroups': r"\bazure\.mgmt\.resource\b",
        }
        for resource_type, pat in azure_patterns.items():
            if re.search(pat, content):
                self.resources[resource_type].append(resource_type)

    def get_file_extensions(self) -> List[str]:
        return ['.py']
