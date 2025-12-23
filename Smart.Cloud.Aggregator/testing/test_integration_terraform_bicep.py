#!/usr/bin/env python3
"""
Integration Tests - Terraform vs Bicep Comparison

Tests to ensure Terraform and Bicep parsers produce equivalent outcomes
for the same infrastructure definitions.
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


class TestTerraformBicepEquivalence(unittest.TestCase):
    """Test that Terraform and Bicep produce equivalent results"""

    def setUp(self):
        """Set up test fixtures"""
        self.tf_dir = tempfile.mkdtemp()
        self.bicep_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.tf_dir, ignore_errors=True)
        shutil.rmtree(self.bicep_dir, ignore_errors=True)

    def create_tf_file(self, directory, filename, content):
        """Helper to create Terraform file"""
        filepath = Path(directory) / filename
        filepath.write_text(content)
        return filepath

    def create_bicep_file(self, directory, filename, content):
        """Helper to create Bicep file"""
        filepath = Path(directory) / filename
        filepath.write_text(content)
        return filepath

    def test_storage_account_equivalence(self):
        """Test Terraform and Bicep produce same result for storage account"""
        # Terraform version
        tf_content = '''
        resource "azurerm_storage_account" "main" {
          name                     = "mystorageaccount"
          resource_group_name      = "my-rg"
          location                 = "eastus"
          account_tier             = "Standard"
          account_replication_type = "LRS"
        }
        '''
        self.create_tf_file(self.tf_dir, "storage.tf", tf_content)
        
        # Bicep version
        bicep_content = '''
        resource storage 'Microsoft.Storage/storageAccounts@2021-04-01' = {
          name: 'mystorageaccount'
          location: 'eastus'
          kind: 'StorageV2'
          sku: {
            name: 'Standard_LRS'
          }
        }
        '''
        self.create_bicep_file(self.bicep_dir, "storage.bicep", bicep_content)
        
        # Parse both
        tf_parser = TerraformParser()
        tf_result = tf_parser.parse_files(self.tf_dir)
        
        bicep_parser = BicepParser()
        bicep_result = bicep_parser.parse_files(self.bicep_dir)
        
        # Both should have Storage category
        self.assertIn('Storage', tf_result)
        self.assertIn('Storage', bicep_result)
        
        # Both should have Storage Account service
        self.assertIn('Storage Account', tf_result['Storage'])
        self.assertIn('Storage Account', bicep_result['Storage'])
        
        # Both should count 1 resource
        self.assertEqual(tf_result['Storage']['Storage Account']['count'], 1)
        self.assertEqual(bicep_result['Storage']['Storage Account']['count'], 1)

    def test_sql_server_equivalence(self):
        """Test Terraform and Bicep produce same result for SQL Server"""
        # Terraform version
        tf_content = '''
        resource "azurerm_sql_server" "main" {
          name                         = "mysqlserver"
          resource_group_name          = "my-rg"
          location                     = "eastus"
          version                      = "12.0"
          administrator_login          = "sqladmin"
          administrator_login_password = "P@ssw0rd1234"
        }
        '''
        self.create_tf_file(self.tf_dir, "database.tf", tf_content)
        
        # Bicep version
        bicep_content = '''
        resource sqlServer 'Microsoft.Sql/servers@2019-06-01' = {
          name: 'mysqlserver'
          location: 'eastus'
          properties: {
            administratorLogin: 'sqladmin'
            version: '12.0'
          }
        }
        '''
        self.create_bicep_file(self.bicep_dir, "database.bicep", bicep_content)
        
        # Parse both
        tf_parser = TerraformParser()
        tf_result = tf_parser.parse_files(self.tf_dir)
        
        bicep_parser = BicepParser()
        bicep_result = bicep_parser.parse_files(self.bicep_dir)
        
        # Both should have Database category
        self.assertIn('Database', tf_result)
        self.assertIn('Database', bicep_result)
        
        # Both should have SQL Server service
        self.assertIn('SQL Server', tf_result['Database'])
        self.assertIn('SQL Server', bicep_result['Database'])
        
        # Both should count 1 resource
        self.assertEqual(tf_result['Database']['SQL Server']['count'], 1)
        self.assertEqual(bicep_result['Database']['SQL Server']['count'], 1)

    def test_virtual_network_equivalence(self):
        """Test Terraform and Bicep produce same result for virtual network"""
        # Terraform version
        tf_content = '''
        resource "azurerm_virtual_network" "main" {
          name                = "myvnet"
          address_space       = ["10.0.0.0/16"]
          location            = "eastus"
          resource_group_name = "my-rg"

          subnet {
            name           = "subnet1"
            address_prefix = "10.0.1.0/24"
          }
        }
        '''
        self.create_tf_file(self.tf_dir, "network.tf", tf_content)
        
        # Bicep version
        bicep_content = '''
        resource vnet 'Microsoft.Network/virtualNetworks@2021-02-01' = {
          name: 'myvnet'
          location: 'eastus'
          properties: {
            addressSpace: {
              addressPrefixes: [
                '10.0.0.0/16'
              ]
            }
            subnets: [
              {
                name: 'subnet1'
                properties: {
                  addressPrefix: '10.0.1.0/24'
                }
              }
            ]
          }
        }
        '''
        self.create_bicep_file(self.bicep_dir, "network.bicep", bicep_content)
        
        # Parse both
        tf_parser = TerraformParser()
        tf_result = tf_parser.parse_files(self.tf_dir)
        
        bicep_parser = BicepParser()
        bicep_result = bicep_parser.parse_files(self.bicep_dir)
        
        # Both should have Networking category
        self.assertIn('Networking', tf_result)
        self.assertIn('Networking', bicep_result)
        
        # Both should have Virtual Network service
        self.assertIn('Virtual Network', tf_result['Networking'])
        self.assertIn('Virtual Network', bicep_result['Networking'])
        
        # Both should count 1 resource
        self.assertEqual(tf_result['Networking']['Virtual Network']['count'], 1)
        self.assertEqual(bicep_result['Networking']['Virtual Network']['count'], 1)

    def test_multiple_resources_equivalence(self):
        """Test Terraform and Bicep with multiple resources"""
        # Terraform version
        tf_content = '''
        resource "azurerm_storage_account" "main" {
          name                     = "mystorageaccount"
          location                 = "eastus"
        }
        
        resource "azurerm_sql_server" "main" {
          name                         = "mysqlserver"
          location                     = "eastus"
          administrator_login          = "sqladmin"
        }
        
        resource "azurerm_virtual_network" "main" {
          name                = "myvnet"
          address_space       = ["10.0.0.0/16"]
          location            = "eastus"
        }
        '''
        self.create_tf_file(self.tf_dir, "infrastructure.tf", tf_content)
        
        # Bicep version
        bicep_content = '''
        resource storage 'Microsoft.Storage/storageAccounts@2021-04-01' = {
          name: 'mystorageaccount'
          location: 'eastus'
        }
        
        resource sqlServer 'Microsoft.Sql/servers@2019-06-01' = {
          name: 'mysqlserver'
          location: 'eastus'
        }
        
        resource vnet 'Microsoft.Network/virtualNetworks@2021-02-01' = {
          name: 'myvnet'
          location: 'eastus'
        }
        '''
        self.create_bicep_file(self.bicep_dir, "infrastructure.bicep", bicep_content)
        
        # Parse both
        tf_parser = TerraformParser()
        tf_result = tf_parser.parse_files(self.tf_dir)
        
        bicep_parser = BicepParser()
        bicep_result = bicep_parser.parse_files(self.bicep_dir)
        
        # Both should have 3 categories
        self.assertEqual(len(tf_result), 3)
        self.assertEqual(len(bicep_result), 3)
        
        # Both should have Storage, Database, Networking
        for result in [tf_result, bicep_result]:
            self.assertIn('Storage', result)
            self.assertIn('Database', result)
            self.assertIn('Networking', result)


class TestUnifiedParserConsistency(unittest.TestCase):
    """Test unified parser consistency"""

    def setUp(self):
        """Set up test fixtures"""
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

    def test_unified_parser_terraform_only(self):
        """Test unified parser with Terraform only"""
        content = '''
        resource "azurerm_storage_account" "main" {
          name     = "storage1"
          location = "eastus"
        }
        
        resource "azurerm_storage_account" "secondary" {
          name     = "storage2"
          location = "westus"
        }
        '''
        self.create_tf_file("storage.tf", content)
        
        parser = UnifiedIaCParser()
        result = parser.parse_directory(self.test_dir)
        
        self.assertIn('Storage', result)
        self.assertEqual(result['Storage']['Storage Account']['count'], 2)

    def test_unified_parser_bicep_only(self):
        """Test unified parser with Bicep only"""
        content = '''
        resource storage1 'Microsoft.Storage/storageAccounts@2021-04-01' = {
          name: 'storage1'
          location: 'eastus'
        }
        
        resource storage2 'Microsoft.Storage/storageAccounts@2021-04-01' = {
          name: 'storage2'
          location: 'westus'
        }
        '''
        self.create_bicep_file("storage.bicep", content)
        
        parser = UnifiedIaCParser()
        result = parser.parse_directory(self.test_dir)
        
        self.assertIn('Storage', result)
        self.assertEqual(result['Storage']['Storage Account']['count'], 2)

    def test_unified_parser_mixed_formats(self):
        """Test unified parser with both Terraform and Bicep"""
        tf_content = '''
        resource "azurerm_storage_account" "main" {
          name     = "tfstorageaccount"
          location = "eastus"
        }
        '''
        
        bicep_content = '''
        resource storage 'Microsoft.Storage/storageAccounts@2021-04-01' = {
          name: 'bicepstorageaccount'
          location: 'westus'
        }
        '''
        
        self.create_tf_file("terraform.tf", tf_content)
        self.create_bicep_file("bicep.bicep", bicep_content)
        
        parser = UnifiedIaCParser()
        result = parser.parse_directory(self.test_dir)
        
        # Should find Storage category
        self.assertIn('Storage', result)
        
        # Should count 2 storage accounts (1 from Terraform, 1 from Bicep)
        self.assertEqual(result['Storage']['Storage Account']['count'], 2)
        
        # Check parsed files
        parsed = parser.get_parsed_files()
        self.assertEqual(len(parsed['terraform']), 1)
        self.assertEqual(len(parsed['bicep']), 1)

    def test_unified_parser_summary_statistics(self):
        """Test unified parser summary statistics"""
        tf_content = '''
        resource "azurerm_storage_account" "main" {
          name     = "storage1"
          location = "eastus"
        }
        
        resource "azurerm_virtual_network" "main" {
          name                = "vnet1"
          address_space       = ["10.0.0.0/16"]
          location            = "eastus"
        }
        '''
        
        bicep_content = '''
        resource sqlServer 'Microsoft.Sql/servers@2019-06-01' = {
          name: 'sqlserver1'
          location: 'eastus'
        }
        '''
        
        self.create_tf_file("terraform.tf", tf_content)
        self.create_bicep_file("bicep.bicep", bicep_content)
        
        parser = UnifiedIaCParser()
        result = parser.parse_directory(self.test_dir)
        summary = parser.get_summary()
        
        # Should have 3 resources total
        self.assertEqual(summary['total_resources'], 3)
        
        # Should have 1 Terraform file
        self.assertEqual(summary['terraform_files'], 1)
        
        # Should have 1 Bicep file
        self.assertEqual(summary['bicep_files'], 1)


class TestReportGenerationFromBoth(unittest.TestCase):
    """Test report generation from Terraform and Bicep"""

    def test_report_from_terraform_and_bicep(self):
        """Test report generation from combined Terraform and Bicep"""
        services = {
            'Storage': {
                'Storage Account': {
                    'resource_type': 'Microsoft.Storage/storageAccounts',
                    'count': 2,
                    'instances': [
                        'Microsoft.Storage/storageAccounts#tfStorage',
                        'Microsoft.Storage/storageAccounts#bicepStorage'
                    ]
                }
            },
            'Database': {
                'SQL Server': {
                    'resource_type': 'Microsoft.Sql/servers',
                    'count': 1,
                    'instances': ['Microsoft.Sql/servers#sqlServer']
                }
            },
            'Networking': {
                'Virtual Network': {
                    'resource_type': 'Microsoft.Network/virtualNetworks',
                    'count': 1,
                    'instances': ['Microsoft.Network/virtualNetworks#vnet']
                }
            }
        }
        
        metadata = {
            'parsed_files': {
                'terraform': ['main.tf', 'network.tf'],
                'bicep': ['storage.bicep', 'database.bicep']
            },
            'resource_groups': ['my-rg', 'prod-rg']
        }
        
        generator = ReportGenerator(services, metadata)
        report = generator.generate_markdown()
        
        # Check report contains expected content
        self.assertIn('# Azure Services Assessment Report', report)
        self.assertIn('## Summary', report)
        self.assertIn('Storage', report)
        self.assertIn('Database', report)
        self.assertIn('Networking', report)
        self.assertIn('Total Resources:** 4', report)
        self.assertIn('Terraform Files', report)
        self.assertIn('Bicep Files', report)

    def test_json_report_from_combined_sources(self):
        """Test JSON report from combined Terraform and Bicep"""
        services = {
            'Storage': {
                'Storage Account': {
                    'resource_type': 'Microsoft.Storage/storageAccounts',
                    'count': 1,
                    'instances': ['Microsoft.Storage/storageAccounts#storage']
                }
            }
        }
        
        metadata = {
            'parsed_files': {
                'terraform': ['main.tf'],
                'bicep': ['storage.bicep']
            }
        }
        
        generator = ReportGenerator(services, metadata)
        json_report = generator.generate_json()
        
        # Parse JSON and verify structure
        data = json.loads(json_report)
        
        self.assertIn('generated', data)
        self.assertIn('metadata', data)
        self.assertIn('services', data)
        self.assertIn('summary', data)
        
        # Check metadata
        self.assertEqual(len(data['metadata']['parsed_files']['terraform']), 1)
        self.assertEqual(len(data['metadata']['parsed_files']['bicep']), 1)


class TestParserConsistency(unittest.TestCase):
    """Test consistency between parsers"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_key_vault_terraform_bicep(self):
        """Test Key Vault parsing in Terraform"""
        # Terraform
        tf_content = '''
        resource "azurerm_key_vault" "main" {
          name                       = "mykeyvault"
          location                   = "eastus"
          resource_group_name        = "my-rg"
          tenant_id                  = "12345678-1234-1234-1234-123456789012"
          sku_name                   = "premium"
          enabled_for_disk_encryption = true
        }
        '''
        
        # Create separate directories
        tf_dir = Path(self.test_dir) / "tf"
        tf_dir.mkdir()
        
        (tf_dir / "keyvault.tf").write_text(tf_content)
        
        tf_parser = TerraformParser()
        tf_result = tf_parser.parse_files(str(tf_dir))
        
        # Terraform should recognize Key Vault
        self.assertIn('Security', tf_result)
        self.assertIn('Key Vault', tf_result['Security'])
        self.assertEqual(tf_result['Security']['Key Vault']['count'], 1)
        

def run_integration_tests():
    """Run all integration tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestTerraformBicepEquivalence))
    suite.addTests(loader.loadTestsFromTestCase(TestUnifiedParserConsistency))
    suite.addTests(loader.loadTestsFromTestCase(TestReportGenerationFromBoth))
    suite.addTests(loader.loadTestsFromTestCase(TestParserConsistency))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("INTEGRATION TEST SUMMARY")
    print("="*70)
    print(f"Tests Run:    {result.testsRun}")
    print(f"Successes:    {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures:     {len(result.failures)}")
    print(f"Errors:       {len(result.errors)}")
    print(f"Skipped:      {len(result.skipped)}")
    print("="*70)
    
    if result.wasSuccessful():
        print("? ALL INTEGRATION TESTS PASSED!")
        return 0
    else:
        print("? SOME INTEGRATION TESTS FAILED")
        return 1


if __name__ == '__main__':
    exit(run_integration_tests())
