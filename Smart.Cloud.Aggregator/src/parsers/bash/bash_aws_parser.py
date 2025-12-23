"""
Bash AWS Parser

Parses Bash scripts that use AWS CLI to detect AWS resources.
"""

import re
from pathlib import Path
from typing import Dict, List

from ..base import BaseIaCParser

class BashAWSParser(BaseIaCParser):
    """Parses Bash scripts and extracts AWS CLI resource usage"""

    def parse_files(self, directory: str) -> Dict[str, Dict]:
        p = Path(directory)
        if not p.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        files = list(p.glob('**/*.sh'))
        if not files:
            raise FileNotFoundError(f"No Bash scripts found in {directory}")
        print(f"Found {len(files)} Bash script(s)")
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
        # Detect common AWS CLI create/update commands
        patterns = {
            'aws_s3_bucket': r"aws\s+s3api\s+create-bucket",
            'aws_ec2_instance': r"aws\s+ec2\s+run-instances",
            'aws_lambda_function': r"aws\s+lambda\s+create-function",
            'aws_dynamodb_table': r"aws\s+dynamodb\s+create-table",
            'aws_rds_instance': r"aws\s+rds\s+create-db-instance",
            'aws_opensearch_domain': r"aws\s+opensearch\s+create-domain",
            'aws_redshiftserverless_namespace': r"aws\s+redshift-serverless\s+create-namespace",
            'aws_kinesis_stream': r"aws\s+kinesis\s+create-stream",
            'aws_sns_topic': r"aws\s+sns\s+create-topic",
            'aws_sqs_queue': r"aws\s+sqs\s+create-queue",
            'aws_ecs_cluster': r"aws\s+ecs\s+create-cluster",
            'aws_eks_cluster': r"aws\s+eks\s+create-cluster",
            'aws_cloudwatch_log_group': r"aws\s+logs\s+create-log-group",
            'aws_events_rule': r"aws\s+events\s+put-rule",
            'aws_glue_job': r"aws\s+glue\s+create-job",
            'aws_emr_cluster': r"aws\s+emr\s+create-cluster",
            'aws_appflow_flow': r"aws\s+appflow\s+create-flow",
        }
        for key, pat in patterns.items():
            if re.search(pat, content):
                self.resources[key].append(key)

    def get_file_extensions(self) -> List[str]:
        return ['.sh']
