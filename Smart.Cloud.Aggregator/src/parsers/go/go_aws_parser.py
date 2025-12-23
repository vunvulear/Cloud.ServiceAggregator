"""
Go AWS Parser

Detects AWS SDK usage in Go source files.
"""

import re
from pathlib import Path
from typing import Dict, List

from ..base import BaseIaCParser

class GoAWSParser(BaseIaCParser):
    def parse_files(self, directory: str) -> Dict[str, Dict]:
        p = Path(directory)
        if not p.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        files = list(p.glob('**/*.go'))
        if not files:
            raise FileNotFoundError(f"No Go files found in {directory}")
        print(f"Found {len(files)} Go file(s)")
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
        # Detect AWS SDK v2 service clients
        patterns = {
            'aws_s3_bucket': r"service/s3",
            'aws_lambda_function': r"service/lambda",
            'aws_ec2_instance': r"service/ec2",
            'aws_dynamodb_table': r"service/dynamodb",
            'aws_rds_instance': r"service/rds",
            'aws_kinesis_stream': r"service/kinesis",
            'aws_opensearch_domain': r"service/opensearch",
            'aws_cloudwatch_log_group': r"service/cloudwatchlogs",
            'aws_sns_topic': r"service/sns",
            'aws_sqs_queue': r"service/sqs",
            'aws_eks_cluster': r"service/eks",
            'aws_ecs_cluster': r"service/ecs",
        }
        for key, pat in patterns.items():
            if re.search(pat, content):
                self.resources[key].append(key)

    def get_file_extensions(self) -> List[str]:
        return ['.go']
