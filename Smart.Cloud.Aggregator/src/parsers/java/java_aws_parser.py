"""
Java AWS Parser

Detects AWS SDK usage in Java source files.
"""

import re
from pathlib import Path
from typing import Dict, List

from ..base import BaseIaCParser

class JavaAWSParser(BaseIaCParser):
    def parse_files(self, directory: str) -> Dict[str, Dict]:
        p = Path(directory)
        if not p.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        files = []
        files.extend(p.glob('**/*.java'))
        files.extend(p.glob('**/*.cs'))
        if not files:
            raise FileNotFoundError(f"No Java/C# files found in {directory}")
        print(f"Found {len(files)} Java/C# file(s)")
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
        # Detect AWS SDK client construction in Java or C#
        patterns = {
            'aws_s3_bucket': r"(AmazonS3Client|S3Client)\b",
            'aws_lambda_function': r"(AWSLambdaClient|LambdaClient)\b",
            'aws_ec2_instance': r"(AmazonEC2Client|Ec2Client)\b",
            'aws_dynamodb_table': r"(AmazonDynamoDBClient|DynamoDbClient)\b",
            'aws_rds_instance': r"(AmazonRDSClient|RdsClient)\b",
            'aws_kinesis_stream': r"(AmazonKinesisClient|KinesisClient)\b",
            'aws_opensearch_domain': r"(AmazonOpenSearch|OpenSearchClient)\b",
            'aws_cloudwatch_log_group': r"(AmazonCloudWatchLogs|CloudWatchLogsClient)\b",
            'aws_sns_topic': r"(AmazonSNS|SnsClient)\b",
            'aws_sqs_queue': r"(AmazonSQS|SqsClient)\b",
            'aws_eks_cluster': r"(EksClient)\b",
            'aws_ecs_cluster': r"(EcsClient)\b",
        }
        for key, pat in patterns.items():
            if re.search(pat, content):
                self.resources[key].append(key)

    def get_file_extensions(self) -> List[str]:
        return ['.java', '.cs']
