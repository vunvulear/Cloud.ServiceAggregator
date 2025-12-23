#!/usr/bin/env python3
"""
Comprehensive Unit Tests for Smart Cloud Aggregator

Tests cover:
- TerraformParser functionality
- ReportGenerator functionality
- Resource extraction and aggregation
- Markdown report generation
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
from datetime import datetime

# Import classes from main application
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.aggregator import TerraformParser, ReportGenerator


class TestTerraformParser(unittest.TestCase):
    """Test cases for TerraformParser class"""

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

    def test_parser_initialization(self):
        """Test parser initializes correctly"""
        self.assertIsInstance(self.parser.resources, dict)
        self.assertIsInstance(self.parser.resource_groups, set)
        self.assertEqual(len(self.parser.resources), 0)

    def test_service_mapping_contains_services(self):
        """Test SERVICE_MAPPING has expected services"""
        self.assertIn('azurerm_storage_account', self.parser.SERVICE_MAPPING)
        self.assertIn('azurerm_sql_server', self.parser.SERVICE_MAPPING)
        self.assertIn('azurerm_virtual_network', self.parser.SERVICE_MAPPING)
        self.assertGreater(len(self.parser.SERVICE_MAPPING), 50)

    def test_service_mapping_structure(self):
        """Test SERVICE_MAPPING has correct structure"""
        for resource_type, (category, service) in self.parser.SERVICE_MAPPING.items():
            self.assertIsInstance(resource_type, str)
            self.assertIsInstance(category, str)
            self.assertIsInstance(service, str)
            self.assertTrue(resource_type.startswith('azurerm_'))
            self.assertTrue(len(category) > 0)
            self.assertTrue(len(service) > 0)

    def test_extract_single_resource(self):
        """Test extraction of a single resource"""
        content = '''
        resource "azurerm_storage_account" "test" {
          name = "test"
        }
        '''
        self.parser._extract_resources(content, Path("test.tf"))
        
        self.assertIn('azurerm_storage_account', self.parser.resources)
        self.assertEqual(len(self.parser.resources['azurerm_storage_account']), 1)
        self.assertIn('azurerm_storage_account.test', 
                     self.parser.resources['azurerm_storage_account'])

    def test_extract_multiple_resources(self):
        """Test extraction of multiple resources"""
        content = '''
        resource "azurerm_storage_account" "test1" {
          name = "test1"
        }
        resource "azurerm_storage_account" "test2" {
          name = "test2"
        }
        resource "azurerm_sql_server" "db" {
          name = "db"
        }
        '''
        self.parser._extract_resources(content, Path("test.tf"))
        
        self.assertEqual(len(self.parser.resources['azurerm_storage_account']), 2)
        self.assertEqual(len(self.parser.resources['azurerm_sql_server']), 1)

    def test_extract_ignores_non_azure_resources(self):
        """Test that non-Azure resources are ignored"""
        content = '''
        resource "aws_s3_bucket" "test" {
          name = "test"
        }
        resource "azurerm_storage_account" "test" {
          name = "test"
        }
        '''
        self.parser._extract_resources(content, Path("test.tf"))
        
        self.assertNotIn('aws_s3_bucket', self.parser.resources)
        self.assertIn('azurerm_storage_account', self.parser.resources)

    def test_extract_resource_group_from_section(self):
        """Test extraction of resource group name"""
        section = '''
        {
          name = "test"
          resource_group_name = "my-rg"
          location = "East US"
        }
        '''
        rg = self.parser._extract_resource_group(section)
        self.assertEqual(rg, "my-rg")

    def test_extract_resource_group_with_variable(self):
        """Test extraction when resource group uses variable"""
        section = '''
        {
          resource_group_name = azurerm_resource_group.main.name
        }
        '''
        rg = self.parser._extract_resource_group(section)
        self.assertEqual(rg, "azurerm_resource_group.main.name")

    def test_extract_resource_group_missing(self):
        """Test extraction when resource group is missing"""
        section = '''
        {
          name = "test"
          location = "East US"
        }
        '''
        rg = self.parser._extract_resource_group(section)
        self.assertEqual(rg, "")

    def test_parse_terraform_directory(self):
        """Test parsing a Terraform directory"""
        tf_content = '''
        resource "azurerm_storage_account" "main" {
          name = "storage"
        }
        resource "azurerm_sql_server" "db" {
          name = "db"
        }
        '''
        self.create_tf_file("main.tf", tf_content)
        
        parser = TerraformParser()
        result = parser.parse_terraform_files(self.test_dir)
        
        self.assertIsInstance(result, dict)
        self.assertIn('Storage', result)
        self.assertIn('Database', result)

    def test_parse_nonexistent_directory(self):
        """Test parsing nonexistent directory raises error"""
        parser = TerraformParser()
        with self.assertRaises(FileNotFoundError):
            parser.parse_terraform_files("/nonexistent/path")

    def test_parse_directory_no_tf_files(self):
        """Test parsing directory with no .tf files raises error"""
        parser = TerraformParser()
        with self.assertRaises(FileNotFoundError):
            parser.parse_terraform_files(self.test_dir)

    def test_aggregate_services(self):
        """Test aggregation of services"""
        content = '''
        resource "azurerm_storage_account" "test1" {
          name = "test1"
        }
        resource "azurerm_storage_account" "test2" {
          name = "test2"
        }
        resource "azurerm_sql_server" "db" {
          name = "db"
        }
        '''
        self.parser._extract_resources(content, Path("test.tf"))
        result = self.parser._aggregate_services()
        
        self.assertIn('Storage', result)
        self.assertIn('Database', result)
        self.assertEqual(result['Storage']['Storage Account']['count'], 2)
        self.assertEqual(result['Database']['SQL Server']['count'], 1)

    def test_aggregate_unmapped_resources(self):
        """Test that unmapped resources don't appear in aggregation"""
        self.parser.resources['azurerm_unknown_service'] = ['instance1']
        result = self.parser._aggregate_services()
        
        # Unknown service should not be in result
        all_services = []
        for category in result.values():
            for service_type in category.values():
                all_services.append(service_type['resource_type'])
        
        self.assertNotIn('azurerm_unknown_service', all_services)

    def test_extract_resource_section(self):
        """Test extraction of resource section"""
        content = '''
        resource "azurerm_storage" "test" {
          name = "test"
          location = "eastus"
        }
        '''
        section = self.parser._extract_resource_section(content, 0)
        self.assertIn('name = "test"', section)
        self.assertIn('location = "eastus"', section)

    def test_complex_terraform_file(self):
        """Test parsing complex Terraform file with comments and formatting"""
        tf_content = '''
        # This is a comment
        resource "azurerm_storage_account" "main" {
          name = "test"
          # Another comment
          resource_group_name = "my-rg"
        }
        
        # Multiple resources
        resource "azurerm_sql_server" "db" {
          name = "database"
        }
        
        resource "azurerm_virtual_network" "vnet" {
          name = "vnet"
        }
        '''
        self.parser._extract_resources(tf_content, Path("complex.tf"))
        
        self.assertEqual(len(self.parser.resources['azurerm_storage_account']), 1)
        self.assertEqual(len(self.parser.resources['azurerm_sql_server']), 1)
        self.assertEqual(len(self.parser.resources['azurerm_virtual_network']), 1)


class TestReportGenerator(unittest.TestCase):
    """Test cases for ReportGenerator class"""

    def setUp(self):
        """Set up test fixtures"""
        self.sample_services = {
            'Compute': {
                'Virtual Machines': {
                    'resource_type': 'azurerm_virtual_machine',
                    'count': 2,
                    'instances': ['azurerm_virtual_machine.vm1', 'azurerm_virtual_machine.vm2']
                },
                'App Service': {
                    'resource_type': 'azurerm_app_service',
                    'count': 1,
                    'instances': ['azurerm_app_service.web']
                }
            },
            'Storage': {
                'Storage Account': {
                    'resource_type': 'azurerm_storage_account',
                    'count': 1,
                    'instances': ['azurerm_storage_account.main']
                }
            }
        }
        self.generator = ReportGenerator(self.sample_services)

    def test_generator_initialization(self):
        """Test report generator initializes correctly"""
        self.assertIsInstance(self.generator.services, dict)
        self.assertEqual(len(self.generator.services), 2)

    def test_generate_markdown(self):
        """Test markdown generation"""
        report = self.generator.generate_markdown()
        
        self.assertIsInstance(report, str)
        self.assertIn('# Azure Services Assessment Report', report)
        self.assertIn('## Summary', report)
        self.assertIn('## Azure Services by Category', report)
        self.assertIn('## Detailed Resource List', report)

    def test_markdown_contains_summary(self):
        """Test generated report contains summary section"""
        report = self.generator.generate_markdown()
        
        self.assertIn('Total Service Categories:** 2', report)
        self.assertIn('Total Azure Services:** 3', report)
        self.assertIn('Total Resources:** 4', report)

    def test_markdown_contains_categories(self):
        """Test generated report contains all categories"""
        report = self.generator.generate_markdown()
        
        self.assertIn('### Compute', report)
        self.assertIn('### Storage', report)

    def test_markdown_contains_services(self):
        """Test generated report contains all services"""
        report = self.generator.generate_markdown()
        
        self.assertIn('Virtual Machines', report)
        self.assertIn('App Service', report)
        self.assertIn('Storage Account', report)

    def test_markdown_contains_instances(self):
        """Test generated report contains resource instances"""
        report = self.generator.generate_markdown()
        
        self.assertIn('azurerm_virtual_machine.vm1', report)
        self.assertIn('azurerm_app_service.web', report)
        self.assertIn('azurerm_storage_account.main', report)

    def test_markdown_contains_resource_types(self):
        """Test generated report contains resource types"""
        report = self.generator.generate_markdown()
        
        self.assertIn('azurerm_virtual_machine', report)
        self.assertIn('azurerm_app_service', report)
        self.assertIn('azurerm_storage_account', report)

    def test_header_contains_timestamp(self):
        """Test header contains timestamp"""
        header = self.generator._header()
        
        self.assertIn('Generated:', header)
        # Check that timestamp matches format
        date_str = datetime.now().strftime("%Y-%m-%d")
        self.assertIn(date_str, header)

    def test_summary_calculation(self):
        """Test summary calculations are correct"""
        summary = self.generator._summary()
        
        self.assertIn('Total Service Categories:** 2', summary)
        self.assertIn('Total Azure Services:** 3', summary)
        self.assertIn('Total Resources:** 4', summary)

    def test_empty_services(self):
        """Test report generation with empty services"""
        generator = ReportGenerator({})
        report = generator.generate_markdown()
        
        self.assertIn('Total Service Categories:** 0', report)
        self.assertIn('Total Azure Services:** 0', report)
        self.assertIn('Total Resources:** 0', report)

    def test_single_service(self):
        """Test report generation with single service"""
        services = {
            'Compute': {
                'Virtual Machines': {
                    'resource_type': 'azurerm_virtual_machine',
                    'count': 1,
                    'instances': ['azurerm_virtual_machine.vm1']
                }
            }
        }
        generator = ReportGenerator(services)
        report = generator.generate_markdown()
        
        self.assertIn('Total Service Categories:** 1', report)
        self.assertIn('Total Azure Services:** 1', report)
        self.assertIn('Total Resources:** 1', report)

    def test_markdown_format(self):
        """Test markdown contains proper formatting"""
        report = self.generator.generate_markdown()
        
        # Check for markdown headers
        self.assertIn('#', report)
        # Check for markdown lists
        self.assertIn('-', report)
        # Check for markdown bold
        self.assertIn('**', report)
        # Check for markdown code
        self.assertIn('`', report)

    def test_footer_present(self):
        """Test footer is included in report"""
        report = self.generator.generate_markdown()
        
        self.assertIn('automatically generated', report)
        self.assertIn('Terraform configurations', report)

    def test_services_sorted(self):
        """Test that services are sorted in output"""
        report = self.generator.generate_markdown()
        
        # Check that Compute comes before Storage in the report
        compute_pos = report.find('### Compute')
        storage_pos = report.find('### Storage')
        self.assertGreater(storage_pos, compute_pos)


class TestIntegration(unittest.TestCase):
    """Integration tests combining Parser and Generator"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def create_tf_file(self, filename, content):
        """Helper method to create test Terraform files"""
        filepath = Path(self.test_dir) / filename
        filepath.write_text(content)
        return filepath

    def test_end_to_end_parsing_and_reporting(self):
        """Test complete workflow from parsing to report generation"""
        tf_content = '''
        resource "azurerm_storage_account" "main" {
          name = "storage"
        }
        resource "azurerm_sql_server" "db" {
          name = "database"
        }
        resource "azurerm_virtual_network" "vnet" {
          name = "vnet"
        }
        '''
        self.create_tf_file("main.tf", tf_content)
        
        parser = TerraformParser()
        aggregated = parser.parse_terraform_files(self.test_dir)
        
        generator = ReportGenerator(aggregated)
        report = generator.generate_markdown()
        
        self.assertIn('Storage', report)
        self.assertIn('Database', report)
        self.assertIn('Networking', report)
        self.assertIn('Total Resources:** 3', report)

    def test_multiple_files_parsing(self):
        """Test parsing multiple Terraform files"""
        tf_content1 = '''
        resource "azurerm_storage_account" "main" {
          name = "storage"
        }
        '''
        tf_content2 = '''
        resource "azurerm_sql_server" "db" {
          name = "database"
        }
        '''
        self.create_tf_file("storage.tf", tf_content1)
        self.create_tf_file("database.tf", tf_content2)
        
        parser = TerraformParser()
        aggregated = parser.parse_terraform_files(self.test_dir)
        
        total_resources = sum(
            service['count'] for category in aggregated.values()
            for service in category.values()
        )
        
        self.assertEqual(total_resources, 2)

    def test_report_save_to_file(self):
        """Test saving report to file"""
        tf_content = '''
        resource "azurerm_storage_account" "main" {
          name = "storage"
        }
        '''
        self.create_tf_file("main.tf", tf_content)
        
        parser = TerraformParser()
        aggregated = parser.parse_terraform_files(self.test_dir)
        generator = ReportGenerator(aggregated)
        
        output_file = Path(self.test_dir) / "report.md"
        generator.save_to_file(str(output_file))
        
        self.assertTrue(output_file.exists())
        content = output_file.read_text()
        self.assertIn('# Azure Services Assessment Report', content)
        self.assertIn('Azure Services Assessment Report', content)

    def test_json_export(self):
        """Test JSON export functionality"""
        tf_content = '''
        resource "azurerm_storage_account" "main" {
          name = "storage"
        }
        '''
        self.create_tf_file("main.tf", tf_content)
        
        parser = TerraformParser()
        aggregated = parser.parse_terraform_files(self.test_dir)
        
        # Simulate JSON export
        json_str = json.dumps(aggregated)
        json_data = json.loads(json_str)
        
        self.assertIn('Storage', json_data)
        self.assertIsInstance(json_data['Storage'], dict)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""

    def setUp(self):
        """Set up test fixtures"""
        self.parser = TerraformParser()

    def test_malformed_resource_declaration(self):
        """Test handling of malformed resource declarations"""
        content = '''
        resource "azurerm_storage" {
          name = "test"
        }
        '''
        # Should not raise exception
        self.parser._extract_resources(content, Path("test.tf"))
        self.assertEqual(len(self.parser.resources), 0)

    def test_nested_resource_blocks(self):
        """Test handling of nested resource blocks"""
        content = '''
        resource "azurerm_storage_account" "main" {
          name = "test"
          blob_properties {
            cors_rule {
              allowed_headers = ["*"]
            }
          }
        }
        '''
        self.parser._extract_resources(content, Path("test.tf"))
        self.assertIn('azurerm_storage_account', self.parser.resources)

    def test_special_characters_in_names(self):
        """Test handling of special characters in resource names"""
        content = '''
        resource "azurerm_storage_account" "test_name_123" {
          name = "test"
        }
        '''
        self.parser._extract_resources(content, Path("test.tf"))
        self.assertIn('azurerm_storage_account.test_name_123', 
                     self.parser.resources['azurerm_storage_account'])

    def test_quoted_resource_names(self):
        """Test handling of quoted resource names"""
        content = '''
        resource "azurerm_storage_account" "my-storage" {
          name = "test"
        }
        '''
        self.parser._extract_resources(content, Path("test.tf"))
        self.assertIn('azurerm_storage_account.my-storage', 
                     self.parser.resources['azurerm_storage_account'])

    def test_empty_terraform_file(self):
        """Test handling of empty Terraform file"""
        content = ""
        self.parser._extract_resources(content, Path("test.tf"))
        self.assertEqual(len(self.parser.resources), 0)

    def test_terraform_comments(self):
        """Test that comments don't affect parsing"""
        content = '''
        # This is a resource
        resource "azurerm_storage_account" "main" {
          # This is a property
          name = "test"
        }
        '''
        self.parser._extract_resources(content, Path("test.tf"))
        self.assertEqual(len(self.parser.resources['azurerm_storage_account']), 1)


def run_tests_with_coverage():
    """Run tests and display results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestTerraformParser))
    suite.addTests(loader.loadTestsFromTestCase(TestReportGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    # Run tests with verbosity
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
    exit(run_tests_with_coverage())
