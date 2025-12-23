#!/usr/bin/env python3
import os
import tempfile
import unittest
from pathlib import Path

from src.parsers.terraform import TerraformParser
from src.parsers.cloudformation import CloudFormationParser
from src.parsers.python import PythonAWSParser
from src.parsers.bash import BashAWSParser
from src.service_mapping import SERVICE_MAPPING

class TestAWSSupport(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel, content):
        p = self.dir / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding='utf-8')
        return p

    # Terraform
    def test_terraform_aws_instance_detected(self):
        tf = '''
        resource "aws_instance" "web" {
          ami           = "ami-123456"
          instance_type = "t3.micro"
        }
        '''
        self.write('main.tf', tf)
        parser = TerraformParser()
        result = parser.parse_files(str(self.dir))
        # aws_instance should be mapped to Compute/EC2 Instance
        self.assertIn('Compute', result)
        self.assertIn('EC2 Instance', result['Compute'])
        info = result['Compute']['EC2 Instance']
        self.assertEqual(info['resource_type'], 'aws_instance')
        self.assertEqual(info['count'], 1)

    # CloudFormation JSON
    def test_cloudformation_ec2_instance_detected_json(self):
        cf_json = {
            "Resources": {
                "MyInstance": {"Type": "AWS::EC2::Instance", "Properties": {"ImageId": "ami-123", "InstanceType": "t3.micro"}}
            }
        }
        import json
        self.write('template.json', json.dumps(cf_json))
        parser = CloudFormationParser()
        result = parser.parse_files(str(self.dir))
        # maps to aws_ec2_instance key
        # Since mapping uses snake conversion, service key stored under resource_type produced
        self.assertIn('Compute', result)
        # Accept either EC2 Instance under Compute
        self.assertIn('EC2 Instance', result['Compute'])
        self.assertEqual(result['Compute']['EC2 Instance']['count'], 1)

    # Python boto3
    def test_python_boto3_s3_detected(self):
        py = '''
import boto3
s3 = boto3.client('s3')
        '''
        self.write('script.py', py)
        parser = PythonAWSParser()
        result = parser.parse_files(str(self.dir))
        self.assertIn('Storage', result)
        self.assertIn('S3 Bucket', result['Storage'])
        self.assertEqual(result['Storage']['S3 Bucket']['count'], 1)

    # Bash aws cli
    def test_bash_aws_cli_ec2_detected(self):
        sh = '''
#!/usr/bin/env bash
aws ec2 run-instances --image-id ami-123 --instance-type t3.micro
        '''
        self.write('create.sh', sh)
        parser = BashAWSParser()
        result = parser.parse_files(str(self.dir))
        self.assertIn('Compute', result)
        # In mapping we used 'aws_ec2_instance' key; category/service from mapping should reflect EC2 Instance
        self.assertIn('EC2 Instance', result['Compute'])
        self.assertEqual(result['Compute']['EC2 Instance']['count'], 1)

if __name__ == '__main__':
    unittest.main()
