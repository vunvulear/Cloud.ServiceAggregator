"""
TypeScript AWS/Azure Parser

Detects AWS CDK/SDK usage and Azure SDK (@azure/arm-*) in TypeScript files.
"""

import re
from pathlib import Path
from typing import Dict, List

from ..base import BaseIaCParser

class TypeScriptAWSParser(BaseIaCParser):
    def parse_files(self, directory: str) -> Dict[str, Dict]:
        p = Path(directory)
        if not p.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        files = []
        files.extend(p.glob('**/*.ts'))
        files.extend(p.glob('**/*.tsx'))
        if not files:
            raise FileNotFoundError(f"No TypeScript files found in {directory}")
        print(f"Found {len(files)} TypeScript file(s)")
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
        # AWS CDK constructs and SDK service clients
        aws_patterns = {
            'aws_s3_bucket': r"new\s+s3\.Bucket\(",
            'aws_lambda_function': r"new\s+lambda\.Function\(",
            'aws_ec2_instance': r"new\s+ec2\.Instance\(",
            'aws_dynamodb_table': r"new\s+dynamodb\.Table\(",
            'aws_rds_instance': r"new\s+rds\.DatabaseInstance\(",
            'aws_kinesis_stream': r"new\s+kinesis\.Stream\(",
            'aws_glue_job': r"new\s+glue.*\(",
            'aws_emr_cluster': r"new\s+emr.*\(",
            'aws_opensearch_domain': r"new\s+opensearch.*Domain\(",
            'aws_redshift_cluster': r"new\s+redshift.*\(",
            'aws_sns_topic': r"new\s+sns\.Topic\(",
            'aws_sqs_queue': r"new\s+sqs\.Queue\(",
            'aws_eks_cluster': r"new\s+eks\.Cluster\(",
            'aws_ecs_cluster': r"new\s+ecs\.Cluster\(",
            # SDK clients
            'aws_s3_bucket_client': r"new\s+S3\(\)",
            'aws_lambda_function_client': r"new\s+Lambda\(\)",
            'aws_ec2_instance_client': r"new\s+EC2\(\)",
            'aws_dynamodb_table_client': r"new\s+DynamoDB\(\)",
            'aws_rds_instance_client': r"new\s+RDS\(\)",
            'aws_kinesis_stream_client': r"new\s+Kinesis\(\)",
            'aws_opensearch_domain_client': r"new\s+OpenSearch\(\)",
            'aws_redshift_cluster_client': r"new\s+Redshift\(\)",
            'aws_sns_topic_client': r"new\s+SNS\(\)",
            'aws_sqs_queue_client': r"new\s+SQS\(\)",
            'aws_cloudwatch_log_group_client': r"new\s+CloudWatchLogs\(\)",
        }
        for key, pat in aws_patterns.items():
            if re.search(pat, content):
                normalized = key.replace('_client', '')
                self.resources[normalized].append(normalized)

        # Azure SDK for JS/TS (@azure/arm-*) common packages -> map to ARM types
        azure_patterns = {
            'Microsoft.Compute/virtualMachines': r"@azure/arm-compute",
            'Microsoft.Network/virtualNetworks': r"@azure/arm-network",
            'Microsoft.Storage/storageAccounts': r"@azure/arm-storage",
            'Microsoft.Web/sites': r"@azure/arm-appservice",
            'Microsoft.ContainerInstance/containerGroups': r"@azure/arm-containerinstance",
            'Microsoft.ContainerService/managedClusters': r"@azure/arm-containerservice",
            'Microsoft.Sql/servers': r"@azure/arm-sql",
            'Microsoft.Resources/resourceGroups': r"@azure/arm-resources",
        }
        for resource_type, pat in azure_patterns.items():
            if re.search(pat, content):
                self.resources[resource_type].append(resource_type)

    def get_file_extensions(self) -> List[str]:
        return ['.ts', '.tsx']
