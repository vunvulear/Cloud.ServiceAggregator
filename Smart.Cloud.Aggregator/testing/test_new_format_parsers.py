#!/usr/bin/env python3
"""
Unit Tests for PowerShell, Azure CLI, and ARM Template Parsers

Comprehensive test coverage for new IaC language support.
"""

import unittest
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.powershell_parser import PowerShellParser
from src.azure_cli_parser import AzureCliParser
from src.arm_template_parser import ArmTemplateParser


class TestPowerShellParser(unittest.TestCase):
    """Test PowerShell parser functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.parser = PowerShellParser()

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def create_ps_file(self, filename, content=""):
        """Helper to create PowerShell file"""
        filepath = Path(self.test_dir) / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content)
        return filepath

    def test_parser_initialization(self):
        """Test PowerShell parser initializes correctly"""
        self.assertIsNotNone(self.parser)
        self.assertGreater(len(self.parser.resource_patterns), 0)

    def test_parse_storage_account(self):
        """Test parsing New-AzStorageAccount"""
        content = '''
        New-AzStorageAccount -Name "mystorageaccount" `
            -ResourceGroupName "myresourcegroup" `
            -Location "eastus" `
            -SkuName "Standard_LRS"
        '''
        self.create_ps_file("storage.ps1", content)
        
        result = self.parser.parse_files(self.test_dir)
        
        self.assertIn('Storage', result)
        self.assertIn('Storage Account', result['Storage'])
        self.assertEqual(result['Storage']['Storage Account']['count'], 1)

    def test_parse_sql_server(self):
        """Test parsing New-AzSqlServer"""
        content = '''
        New-AzSqlServer -ResourceGroupName "myresourcegroup" `
            -ServerName "myserver" `
            -Location "eastus" `
            -SqlAdministratorCredentials $cred
        '''
        self.create_ps_file("database.ps1", content)
        
        result = self.parser.parse_files(self.test_dir)
        
        self.assertIn('Database', result)
        self.assertIn('SQL Server', result['Database'])
        self.assertEqual(result['Database']['SQL Server']['count'], 1)

    def test_parse_keyvault(self):
        """Test parsing New-AzKeyVault"""
        content = '''
        New-AzKeyVault -Name "mykeyvault" `
            -ResourceGroupName "myresourcegroup" `
            -Location "eastus"
        '''
        self.create_ps_file("keyvault.ps1", content)
        
        result = self.parser.parse_files(self.test_dir)
        
        self.assertIn('Security', result)
        self.assertIn('Key Vault', result['Security'])

    def test_parse_multiple_resources(self):
        """Test parsing multiple resources"""
        content = '''
        New-AzStorageAccount -Name "storage" -ResourceGroupName "rg" -Location "eastus"
        New-AzSqlServer -ServerName "server" -ResourceGroupName "rg" -Location "eastus"
        New-AzVirtualNetwork -Name "vnet" -ResourceGroupName "rg" -Location "eastus"
        '''
        self.create_ps_file("multi.ps1", content)
        
        result = self.parser.parse_files(self.test_dir)
        
        self.assertGreaterEqual(len(result), 3)

    def test_remove_comments(self):
        """Test comment removal"""
        content = '''
        # This is a comment
        New-AzStorageAccount -Name "storage" `  # inline comment
            -ResourceGroupName "rg" `
            -Location "eastus"
        '''
        self.create_ps_file("comments.ps1", content)
        
        result = self.parser.parse_files(self.test_dir)
        
        # Should parse successfully even with comments
        self.assertIn('Storage', result)

    def test_extract_resource_groups(self):
        """Test extracting resource group names"""
        content = '''
        New-AzStorageAccount -ResourceGroupName "prod-rg" -Name "storage"
        New-AzSqlServer -ResourceGroup "dev-rg" -ServerName "server"
        '''
        self.create_ps_file("rgs.ps1", content)
        
        self.parser.parse_files(self.test_dir)
        rgs = self.parser.get_resource_groups()
        
        self.assertIn('prod-rg', rgs)
        self.assertIn('dev-rg', rgs)

    def test_parse_nonexistent_directory(self):
        """Test parsing nonexistent directory"""
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_files("/nonexistent")

    def test_parse_no_ps1_files(self):
        """Test parsing directory with no .ps1 files"""
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_files(self.test_dir)


class TestAzureCliParser(unittest.TestCase):
    """Test Azure CLI parser functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.parser = AzureCliParser()

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def create_sh_file(self, filename, content=""):
        """Helper to create shell script file"""
        filepath = Path(self.test_dir) / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content)
        return filepath

    def test_parser_initialization(self):
        """Test Azure CLI parser initializes correctly"""
        self.assertIsNotNone(self.parser)

    def test_parse_storage_account(self):
        """Test parsing storage account creation"""
        content = '''
        #!/bin/bash
        az storage account create \\
            --name "mystorageaccount" \\
            --resource-group "myresourcegroup" \\
            --location "eastus" \\
            --sku "Standard_LRS"
        '''
        self.create_sh_file("storage.sh", content)
        
        result = self.parser.parse_files(self.test_dir)
        
        self.assertIn('Storage', result)

    def test_parse_sql_server(self):
        """Test parsing SQL server creation"""
        content = '''
        #!/bin/bash
        az sql server create \\
            --name "myserver" \\
            --resource-group "myresourcegroup" \\
            --location "eastus" \\
            --admin-user "sqladmin"
        '''
        self.create_sh_file("database.sh", content)
        
        result = self.parser.parse_files(self.test_dir)
        
        self.assertIn('Database', result)

    def test_parse_keyvault(self):
        """Test parsing key vault creation"""
        content = '''
        #!/bin/bash
        az keyvault create \\
            --name "mykeyvault" \\
            --resource-group "myresourcegroup" \\
            --location "eastus"
        '''
        self.create_sh_file("keyvault.sh", content)
        
        result = self.parser.parse_files(self.test_dir)
        
        self.assertIn('Security', result)

    def test_parse_multiple_resources(self):
        """Test parsing multiple resources"""
        content = '''
        #!/bin/bash
        az storage account create -n "storage" -g "rg" -l "eastus"
        az sql server create -n "server" -g "rg" -l "eastus"
        az keyvault create -n "vault" -g "rg" -l "eastus"
        '''
        self.create_sh_file("multi.sh", content)
        
        result = self.parser.parse_files(self.test_dir)
        
        self.assertGreaterEqual(len(result), 2)

    def test_remove_comments(self):
        """Test comment removal from bash"""
        content = '''
        #!/bin/bash
        # Create storage account
        az storage account create \\
            --name "storage" \\  # storage name
            -g "rg"
        '''
        self.create_sh_file("comments.sh", content)
        
        result = self.parser.parse_files(self.test_dir)
        
        # Should parse successfully
        self.assertIn('Storage', result)

    def test_extract_resource_groups(self):
        """Test extracting resource group names"""
        content = '''
        #!/bin/bash
        az storage account create -n "storage" --resource-group "prod-rg"
        az sql server create -n "server" -g "dev-rg"
        '''
        self.create_sh_file("rgs.sh", content)
        
        self.parser.parse_files(self.test_dir)
        rgs = self.parser.get_resource_groups()
        
        self.assertIn('prod-rg', rgs)
        self.assertIn('dev-rg', rgs)

    def test_parse_nonexistent_directory(self):
        """Test parsing nonexistent directory"""
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_files("/nonexistent")

    def test_parse_no_sh_files(self):
        """Test parsing directory with no .sh files"""
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_files(self.test_dir)


class TestArmTemplateParser(unittest.TestCase):
    """Test ARM template parser functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.parser = ArmTemplateParser()

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def create_arm_file(self, filename, content=""):
        """Helper to create ARM template file"""
        filepath = Path(self.test_dir) / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content)
        return filepath

    def test_parser_initialization(self):
        """Test ARM template parser initializes correctly"""
        self.assertIsNotNone(self.parser)

    def test_parse_storage_account_template(self):
        """Test parsing storage account ARM template"""
        content = '''{
          "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
          "contentVersion": "1.0.0.0",
          "resources": [
            {
              "type": "Microsoft.Storage/storageAccounts",
              "apiVersion": "2021-04-01",
              "name": "mystorageaccount",
              "location": "eastus",
              "sku": {"name": "Standard_LRS"},
              "kind": "StorageV2"
            }
          ]
        }'''
        self.create_arm_file("storage.json", content)
        
        result = self.parser.parse_files(self.test_dir)
        
        self.assertIn('Storage', result)
        self.assertIn('Storage Account', result['Storage'])

    def test_parse_multiple_resources_template(self):
        """Test parsing template with multiple resources"""
        content = '''{
          "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
          "contentVersion": "1.0.0.0",
          "resources": [
            {"type": "Microsoft.Storage/storageAccounts", "apiVersion": "2021-04-01", "name": "storage", "location": "eastus"},
            {"type": "Microsoft.Sql/servers", "apiVersion": "2019-06-01", "name": "server", "location": "eastus"},
            {"type": "Microsoft.KeyVault/vaults", "apiVersion": "2021-06-01", "name": "vault", "location": "eastus"}
          ]
        }'''
        self.create_arm_file("multi.json", content)
        
        result = self.parser.parse_files(self.test_dir)
        
        self.assertEqual(len(result), 3)

    def test_detect_arm_template(self):
        """Test ARM template detection"""
        arm_content = '''{
          "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
          "resources": []
        }'''
        
        non_arm_content = '{"name": "test"}'
        
        arm_file = self.create_arm_file("arm.json", arm_content)
        non_arm_file = self.create_arm_file("other.json", non_arm_content)
        
        self.assertTrue(self.parser._is_arm_template(arm_file))
        self.assertFalse(self.parser._is_arm_template(non_arm_file))

    def test_parse_nonexistent_directory(self):
        """Test parsing nonexistent directory"""
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_files("/nonexistent")

    def test_parse_no_templates(self):
        """Test parsing directory with no ARM templates"""
        # Create non-ARM JSON file
        content = '{"test": "data"}'
        self.create_arm_file("notarm.json", content)
        
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_files(self.test_dir)


class TestMultiFormatParsing(unittest.TestCase):
    """Test parsing multiple formats in same directory"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_parse_all_formats(self):
        """Test parsing PowerShell, CLI, and ARM in same structure"""
        # Create test files
        Path(self.test_dir, "scripts").mkdir()
        Path(self.test_dir, "templates").mkdir()
        
        # PowerShell
        ps_content = 'New-AzStorageAccount -Name "ps-storage" -ResourceGroupName "rg"'
        (Path(self.test_dir) / "scripts" / "storage.ps1").write_text(ps_content)
        
        # Bash
        sh_content = '#!/bin/bash\naz storage account create --name "bash-storage" -g "rg"'
        (Path(self.test_dir) / "scripts" / "storage.sh").write_text(sh_content)
        
        # ARM
        arm_content = '''{
          "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
          "resources": [
            {"type": "Microsoft.Storage/storageAccounts", "apiVersion": "2021-04-01", "name": "arm-storage"}
          ]
        }'''
        (Path(self.test_dir) / "templates" / "storage.json").write_text(arm_content)
        
        # Parse each
        ps_parser = PowerShellParser()
        cli_parser = AzureCliParser()
        arm_parser = ArmTemplateParser()
        
        ps_result = ps_parser.parse_files(str(Path(self.test_dir) / "scripts"))
        cli_result = cli_parser.parse_files(str(Path(self.test_dir) / "scripts"))
        arm_result = arm_parser.parse_files(str(Path(self.test_dir) / "templates"))
        
        # All should find storage accounts
        self.assertIn('Storage', ps_result)
        self.assertIn('Storage', cli_result)
        self.assertIn('Storage', arm_result)


def run_new_parser_tests():
    """Run all new parser tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestPowerShellParser))
    suite.addTests(loader.loadTestsFromTestCase(TestAzureCliParser))
    suite.addTests(loader.loadTestsFromTestCase(TestArmTemplateParser))
    suite.addTests(loader.loadTestsFromTestCase(TestMultiFormatParsing))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*70)
    print("NEW FORMAT PARSERS TEST SUMMARY")
    print("="*70)
    print(f"Tests Run:    {result.testsRun}")
    print(f"Successes:    {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures:     {len(result.failures)}")
    print(f"Errors:       {len(result.errors)}")
    print(f"Skipped:      {len(result.skipped)}")
    print("="*70)
    
    if result.wasSuccessful():
        print("? ALL NEW PARSER TESTS PASSED!")
        return 0
    else:
        print("? SOME NEW PARSER TESTS FAILED")
        return 1


if __name__ == '__main__':
    exit(run_new_parser_tests())
