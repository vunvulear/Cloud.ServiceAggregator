#!/usr/bin/env python3
"""
Unit Tests for Smart Cloud Aggregator v2.0

Tests for:
- Terraform Parser
- Bicep Parser  
- Unified Parser
- Report Generator (enhanced)
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.terraform_parser import TerraformParser
from src.bicep_parser import BicepParser
from src.unified_parser import UnifiedIaCParser
from src.report_generator import ReportGenerator
from src.service_mapping import SERVICE_MAPPING, get_service_category, is_azure_resource


class TestServiceMapping(unittest.TestCase):
    """Test the service mapping functionality"""

    def test_service_mapping_contains_azure_resources(self):
        """Test SERVICE_MAPPING contains expected services"""
        self.assertIn('azurerm_storage_account', SERVICE_MAPPING)
        self.assertIn('Microsoft.Storage/storageAccounts', SERVICE_MAPPING)
        self.assertGreater(len(SERVICE_MAPPING), 50)

    def test_get_service_category_terraform(self):
        """Test getting service category for Terraform resource"""
        category, service = get_service_category('azurerm_storage_account')
        self.assertEqual(category, 'Storage')
        self.assertEqual(service, 'Storage Account')

    def test_get_service_category_bicep(self):
        """Test getting service category for Bicep resource"""
        category, service = get_service_category('Microsoft.Storage/storageAccounts')
        self.assertEqual(category, 'Storage')
        self.assertEqual(service, 'Storage Account')

    def test_is_azure_resource_terraform(self):
        """Test is_azure_resource for Terraform resources"""
        self.assertTrue(is_azure_resource('azurerm_storage_account'))
        self.assertFalse(is_azure_resource('aws_s3_bucket'))

    def test_is_azure_resource_bicep(self):
        """Test is_azure_resource for Bicep resources"""
        self.assertTrue(is_azure_resource('Microsoft.Storage/storageAccounts'))
        self.assertFalse(is_azure_resource('AWS::S3::Bucket'))


class TestTerraformParser(unittest.TestCase):
    """Test cases for Terraform Parser"""

    def setUp(self):
        """Set up test fixtures"""
        self.parser = TerraformParser()
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def create_tf_file(self, filename, content):
        """Helper method to create test Terraform files"""
        filepath = Path(self.test_dir) / filename
        filepath.write_text(content)
        return filepath

    def test_terraform_single_resource(self):
        """Test parsing single Terraform resource"""
        content = '''
        resource "azurerm_storage_account" "test" {
          name = "test"
        }
        '''
        self.create_tf_file("main.tf", content)
        
        result = self.parser.parse_files(self.test_dir)
        
        self.assertIn('Storage', result)
        self.assertEqual(result['Storage']['Storage Account']['count'], 1)

    def test_terraform_multiple_resources(self):
        """Test parsing multiple Terraform resources"""
        content = '''
        resource "azurerm_storage_account" "test1" {
          name = "test1"
        }
        resource "azurerm_sql_server" "db" {
          name = "db"
        }
        '''
        self.create_tf_file("main.tf", content)
        
        result = self.parser.parse_files(self.test_dir)
        
        self.assertIn('Storage', result)
        self.assertIn('Database', result)

    def test_terraform_ignores_non_azure(self):
        """Test Terraform parser ignores non-Azure resources"""
        content = '''
        resource "aws_s3_bucket" "test" {
          name = "test"
        }
        resource "azurerm_storage_account" "test" {
          name = "test"
        }
        '''
        self.create_tf_file("main.tf", content)
        
        result = self.parser.parse_files(self.test_dir)
        
        self.assertIn('Storage', result)
        self.assertNotIn('AWS', result)


class TestBicepParser(unittest.TestCase):
    """Test cases for Bicep Parser"""

    def setUp(self):
        """Set up test fixtures"""
        self.parser = BicepParser()
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def create_bicep_file(self, filename, content):
        """Helper method to create test Bicep files"""
        filepath = Path(self.test_dir) / filename
        filepath.write_text(content)
        return filepath

    def test_bicep_single_resource(self):
        """Test parsing single Bicep resource"""
        content = '''
        resource storageAccount 'Microsoft.Storage/storageAccounts@2021-04-01' = {
          name: 'mystorageaccount'
          location: 'eastus'
        }
        '''
        self.create_bicep_file("main.bicep", content)
        
        result = self.parser.parse_files(self.test_dir)
        
        self.assertIn('Storage', result)
        self.assertEqual(result['Storage']['Storage Account']['count'], 1)

    def test_bicep_multiple_resources(self):
        """Test parsing multiple Bicep resources"""
        content = '''
        resource storageAccount 'Microsoft.Storage/storageAccounts@2021-04-01' = {
          name: 'mystorageaccount'
        }
        
        resource sqlServer 'Microsoft.Sql/servers@2019-06-01' = {
          name: 'mysqlserver'
        }
        '''
        self.create_bicep_file("main.bicep", content)
        
        result = self.parser.parse_files(self.test_dir)
        
        self.assertIn('Storage', result)
        self.assertIn('Database', result)

    def test_bicep_ignores_non_azure(self):
        """Test Bicep parser ignores non-Azure resources"""
        content = '''
        resource storageAccount 'Microsoft.Storage/storageAccounts@2021-04-01' = {
          name: 'mystorageaccount'
        }
        '''
        self.create_bicep_file("main.bicep", content)
        
        result = self.parser.parse_files(self.test_dir)
        
        self.assertIn('Storage', result)
        # Should only parse Microsoft resources


class TestUnifiedParser(unittest.TestCase):
    """Test cases for Unified Parser"""

    def setUp(self):
        """Set up test fixtures"""
        self.parser = UnifiedIaCParser()
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def create_tf_file(self, filename, content):
        """Helper to create Terraform file"""
        filepath = Path(self.test_dir) / filename
        filepath.write_text(content)
        return filepath

    def create_bicep_file(self, filename, content):
        """Helper to create Bicep file"""
        filepath = Path(self.test_dir) / filename
        filepath.write_text(content)
        return filepath

    def test_unified_terraform_only(self):
        """Test unified parser with Terraform files only"""
        content = '''
        resource "azurerm_storage_account" "test" {
          name = "test"
        }
        '''
        self.create_tf_file("main.tf", content)
        
        result = self.parser.parse_directory(self.test_dir)
        
        self.assertIn('Storage', result)

    def test_unified_bicep_only(self):
        """Test unified parser with Bicep files only"""
        content = '''
        resource storageAccount 'Microsoft.Storage/storageAccounts@2021-04-01' = {
          name: 'mystorageaccount'
        }
        '''
        self.create_bicep_file("main.bicep", content)
        
        result = self.parser.parse_directory(self.test_dir)
        
        self.assertIn('Storage', result)

    def test_unified_mixed_files(self):
        """Test unified parser with both Terraform and Bicep files"""
        tf_content = '''
        resource "azurerm_sql_server" "db" {
          name = "mysqlserver"
        }
        '''
        bicep_content = '''
        resource storage 'Microsoft.Storage/storageAccounts@2021-04-01' = {
          name: 'mystorageaccount'
        }
        '''
        
        self.create_tf_file("main.tf", tf_content)
        self.create_bicep_file("main.bicep", bicep_content)
        
        result = self.parser.parse_directory(self.test_dir)
        
        self.assertIn('Storage', result)
        self.assertIn('Database', result)

    def test_unified_parser_summary(self):
        """Test unified parser summary statistics"""
        tf_content = '''
        resource "azurerm_storage_account" "test" {
          name = "test"
        }
        '''
        self.create_tf_file("main.tf", tf_content)
        
        result = self.parser.parse_directory(self.test_dir)
        summary = self.parser.get_summary()
        
        self.assertEqual(summary['total_resources'], 1)
        self.assertEqual(summary['terraform_files'], 1)
        self.assertEqual(summary['bicep_files'], 0)


class TestReportGenerator(unittest.TestCase):
    """Test cases for Enhanced Report Generator"""

    def setUp(self):
        """Set up test fixtures"""
        self.sample_services = {
            'Storage': {
                'Storage Account': {
                    'resource_type': 'azurerm_storage_account',
                    'count': 2,
                    'instances': ['storage1', 'storage2']
                }
            },
            'Database': {
                'SQL Server': {
                    'resource_type': 'azurerm_sql_server',
                    'count': 1,
                    'instances': ['sqlserver1']
                }
            }
        }
        self.metadata = {
            'parsed_files': {
                'terraform': ['main.tf'],
                'bicep': []
            }
        }
        self.generator = ReportGenerator(self.sample_services, self.metadata)

    def test_generate_markdown_contains_header(self):
        """Test markdown generation includes header"""
        report = self.generator.generate_markdown()
        
        self.assertIn('# Azure Services Assessment Report', report)
        self.assertIn('**Generated:**', report)

    def test_generate_markdown_contains_summary(self):
        """Test markdown includes summary section"""
        report = self.generator.generate_markdown()
        
        self.assertIn('## Summary', report)
        self.assertIn('Total Service Categories:** 2', report)
        self.assertIn('Total Azure Services:** 2', report)
        self.assertIn('Total Resources:** 3', report)

    def test_generate_markdown_contains_metadata(self):
        """Test markdown includes metadata when provided"""
        report = self.generator.generate_markdown()
        
        self.assertIn('## Analysis Metadata', report)
        self.assertIn('Terraform Files', report)

    def test_generate_json(self):
        """Test JSON generation"""
        json_output = self.generator.generate_json()
        data = json.loads(json_output)
        
        self.assertIn('generated', data)
        self.assertIn('metadata', data)
        self.assertIn('services', data)
        self.assertIn('summary', data)

    def test_save_markdown_file(self):
        """Test saving markdown file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "report.md"
            self.generator.save_to_file(str(output_file), format='markdown')
            
            self.assertTrue(output_file.exists())
            content = output_file.read_text()
            self.assertIn('# Azure Services Assessment Report', content)

    def test_save_json_file(self):
        """Test saving JSON file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "report.json"
            self.generator.save_to_file(str(output_file), format='json')
            
            self.assertTrue(output_file.exists())
            content = json.loads(output_file.read_text())
            self.assertIn('summary', content)


def run_tests():
    """Run all tests and display results"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestServiceMapping))
    suite.addTests(loader.loadTestsFromTestCase(TestTerraformParser))
    suite.addTests(loader.loadTestsFromTestCase(TestBicepParser))
    suite.addTests(loader.loadTestsFromTestCase(TestUnifiedParser))
    suite.addTests(loader.loadTestsFromTestCase(TestReportGenerator))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests Run:    {result.testsRun}")
    print(f"Successes:    {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures:     {len(result.failures)}")
    print(f"Errors:       {len(result.errors)}")
    print(f"Skipped:      {len(result.skipped)}")
    print("="*70)
    
    if result.wasSuccessful():
        print("? ALL TESTS PASSED!")
        return 0
    else:
        print("? SOME TESTS FAILED")
        return 1


if __name__ == '__main__':
    exit(run_tests())
