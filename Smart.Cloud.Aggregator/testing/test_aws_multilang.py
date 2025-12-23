#!/usr/bin/env python3
import os
import tempfile
import unittest
from pathlib import Path

from src.parsers.typescript import TypeScriptAWSParser
from src.parsers.go import GoAWSParser
from src.parsers.java import JavaAWSParser
from src.parsers.cloudformation import CloudFormationParser
from src.parsers.python import PythonAWSParser
from src.universal_scanner import create_scanner, IaCLanguage

class TestAWSMultiLanguageParsers(unittest.TestCase):
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

    def test_typescript_aws_cdk_detection(self):
        ts = '''
import * as s3 from 'aws-cdk-lib/aws-s3';
new s3.Bucket(this, 'MyBucket');
'''
        self.write('index.ts', ts)
        parser = TypeScriptAWSParser()
        result = parser.parse_files(str(self.dir))
        self.assertIn('Storage', result)
        self.assertIn('S3 Bucket', result['Storage'])
        self.assertEqual(result['Storage']['S3 Bucket']['count'], 1)

    def test_typescript_azure_sdk_detection(self):
        ts = """
import { ComputeManagementClient } from '@azure/arm-compute';
"""
        self.write('azure.ts', ts)
        parser = TypeScriptAWSParser()
        result = parser.parse_files(str(self.dir))
        self.assertIn('Compute', result)
        self.assertIn('Virtual Machines', result['Compute'])

    def test_go_aws_sdk_detection(self):
        go = '''
package main
import (
  "github.com/aws/aws-sdk-go-v2/service/ec2"
  "github.com/aws/aws-sdk-go-v2/service/s3"
)
'''
        self.write('main.go', go)
        parser = GoAWSParser()
        result = parser.parse_files(str(self.dir))
        self.assertIn('Compute', result)  # ec2
        self.assertIn('EC2 Instance', result['Compute'])
        self.assertIn('Storage', result)  # s3
        self.assertIn('S3 Bucket', result['Storage'])

    def test_java_csharp_aws_sdk_detection(self):
        java = '''
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.ec2.Ec2Client;
class A { S3Client s3; Ec2Client ec2; }
'''
        self.write('App.java', java)
        parser = JavaAWSParser()
        result = parser.parse_files(str(self.dir))
        self.assertIn('Storage', result)
        self.assertIn('S3 Bucket', result['Storage'])
        self.assertIn('Compute', result)
        self.assertIn('EC2 Instance', result['Compute'])

    def test_cloudformation_yaml_detection(self):
        yaml = '''
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
'''
        self.write('template.yaml', yaml)
        parser = CloudFormationParser()
        result = parser.parse_files(str(self.dir))
        self.assertIn('Storage', result)
        self.assertIn('S3 Bucket', result['Storage'])
        self.assertEqual(result['Storage']['S3 Bucket']['count'], 1)

    def test_python_azure_sdk_detection(self):
        py = '''
from azure.mgmt.compute import ComputeManagementClient
'''
        self.write('script.py', py)
        parser = PythonAWSParser()
        result = parser.parse_files(str(self.dir))
        self.assertIn('Compute', result)
        self.assertIn('Virtual Machines', result['Compute'])

    def test_scanner_finds_new_languages(self):
        # create files for TS, Go, Java/C#
        self.write('src/app.ts', 'new s3.Bucket(this, "B")')
        self.write('src/main.go', 'package main\nimport "github.com/aws/aws-sdk-go-v2/service/ec2"')
        self.write('src/App.java', 'class A { }')
        scanner = create_scanner()
        scan = scanner.scan_all(str(self.dir))
        langs = set(scan.supported_languages)
        # At least include TypeScript, Go, Java/C# among others
        self.assertIn('TypeScript', langs)
        self.assertIn('Go', langs)
        self.assertIn('Java/C#', langs)

if __name__ == '__main__':
    unittest.main()
