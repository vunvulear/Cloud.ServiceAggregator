#!/usr/bin/env python3
"""
Universal Scanner Tests

Comprehensive tests for directory scanning and language registry.
"""

import unittest
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.universal_scanner import (
    DirectoryScanner,
    LanguageRegistry,
    LanguageConfig,
    IaCLanguage,
    ScanResult,
    ScannerFactory,
    create_scanner
)


class TestLanguageRegistry(unittest.TestCase):
    """Test language registry functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.registry = LanguageRegistry()

    def test_registry_initialization(self):
        """Test registry initializes with default languages"""
        self.assertIsNotNone(self.registry.get(IaCLanguage.TERRAFORM))
        self.assertIsNotNone(self.registry.get(IaCLanguage.BICEP))

    def test_get_enabled_languages(self):
        """Test retrieving enabled languages"""
        enabled = self.registry.get_enabled_languages()
        
        # By default, Terraform and Bicep should be enabled
        names = [config.name for config in enabled]
        self.assertIn('Terraform', names)
        self.assertIn('Bicep', names)

    def test_disable_language(self):
        """Test disabling a language"""
        self.registry.disable_language(IaCLanguage.TERRAFORM)
        
        enabled = self.registry.get_enabled_languages()
        names = [config.name for config in enabled]
        self.assertNotIn('Terraform', names)

    def test_enable_language(self):
        """Test enabling a language"""
        self.registry.disable_language(IaCLanguage.TERRAFORM)
        self.registry.enable_language(IaCLanguage.TERRAFORM)
        
        enabled = self.registry.get_enabled_languages()
        names = [config.name for config in enabled]
        self.assertIn('Terraform', names)

    def test_register_custom_language(self):
        """Test registering a custom language"""
        custom_config = LanguageConfig(
            name="Custom",
            language=IaCLanguage.HELM,
            file_extensions=[".yaml"],
            description="Custom IaC format"
        )
        
        self.registry.register(custom_config)
        retrieved = self.registry.get(IaCLanguage.HELM)
        
        self.assertEqual(retrieved.name, "Custom")

    def test_get_all_languages(self):
        """Test retrieving all languages"""
        all_langs = self.registry.get_all_languages()
        
        # Should have at least Terraform and Bicep
        self.assertGreaterEqual(len(all_langs), 2)

    def test_language_config_extensions(self):
        """Test language extensions configuration"""
        tf_config = self.registry.get(IaCLanguage.TERRAFORM)
        
        self.assertEqual(tf_config.file_extensions, [".tf"])
        self.assertEqual(tf_config.name, "Terraform")


class TestDirectoryScanner(unittest.TestCase):
    """Test directory scanning functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.scanner = DirectoryScanner()

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def create_file(self, filename, content=""):
        """Helper to create test files"""
        filepath = Path(self.test_dir) / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content)
        return filepath

    def test_scanner_initialization(self):
        """Test scanner initializes correctly"""
        self.assertIsNotNone(self.scanner.registry)
        self.assertGreater(len(self.scanner._excluded_dirs), 0)

    def test_scan_empty_directory(self):
        """Test scanning empty directory"""
        result = self.scanner.scan_all(self.test_dir)
        
        self.assertEqual(result.total_files, 0)
        self.assertEqual(len(result.files_by_language), 0)

    def test_scan_terraform_files(self):
        """Test scanning Terraform files"""
        # Create test Terraform files
        self.create_file("main.tf", "resource 'aws_instance' 'web' {}")
        self.create_file("variables.tf", "variable 'instance_type' {}")
        
        result = self.scanner.scan_all(self.test_dir)
        
        self.assertEqual(result.total_files, 2)
        self.assertIn('Terraform', result.files_by_language)
        self.assertEqual(len(result.get_files_by_language('Terraform')), 2)

    def test_scan_bicep_files(self):
        """Test scanning Bicep files"""
        # Create test Bicep file
        self.create_file("main.bicep", "resource storage 'Microsoft.Storage/storageAccounts@2021-04-01' = {}")
        
        result = self.scanner.scan_all(self.test_dir)
        
        self.assertEqual(result.total_files, 1)
        self.assertIn('Bicep', result.files_by_language)
        self.assertTrue(result.has_files('Bicep'))

    def test_scan_mixed_files(self):
        """Test scanning mixed Terraform and Bicep files"""
        self.create_file("main.tf", "resource 'aws_instance' 'web' {}")
        self.create_file("main.bicep", "resource storage 'Microsoft.Storage/storageAccounts@2021-04-01' = {}")
        
        result = self.scanner.scan_all(self.test_dir)
        
        self.assertEqual(result.total_files, 2)
        self.assertEqual(len(result.supported_languages), 2)
        self.assertIn('Terraform', result.supported_languages)
        self.assertIn('Bicep', result.supported_languages)

    def test_scan_recursive(self):
        """Test recursive directory scanning"""
        # Create nested structure
        self.create_file("level1/main.tf", "resource 'aws_instance' 'web' {}")
        self.create_file("level1/level2/variables.tf", "variable 'count' {}")
        self.create_file("level1/level2/level3/outputs.tf", "output 'id' {}")
        
        result = self.scanner.scan_all(self.test_dir)
        
        self.assertEqual(result.total_files, 3)
        files = result.get_files_by_language('Terraform')
        self.assertEqual(len(files), 3)

    def test_scan_non_recursive(self):
        """Test non-recursive scanning"""
        self.create_file("main.tf", "resource 'aws_instance' 'web' {}")
        self.create_file("nested/main.tf", "resource 'aws_instance' 'web' {}")
        
        result = self.scanner.scan(self.test_dir, recursive=False)
        
        self.assertEqual(result.total_files, 1)

    def test_scan_excluded_directories(self):
        """Test that excluded directories are skipped"""
        self.create_file("main.tf", "resource 'aws_instance' 'web' {}")
        self.create_file(".terraform/main.tf", "excluded")
        self.create_file("__pycache__/main.tf", "excluded")
        
        result = self.scanner.scan_all(self.test_dir)
        
        # Should only find the one non-excluded file
        self.assertEqual(result.total_files, 1)

    def test_scan_custom_excluded_directory(self):
        """Test adding custom excluded directories"""
        self.scanner.add_excluded_directory("custom_exclude")
        
        self.create_file("main.tf", "resource 'aws_instance' 'web' {}")
        self.create_file("custom_exclude/main.tf", "excluded")
        
        result = self.scanner.scan_all(self.test_dir)
        
        self.assertEqual(result.total_files, 1)

    def test_scan_remove_excluded_directory(self):
        """Test removing from excluded directories"""
        self.scanner.add_excluded_directory("custom_exclude")
        self.scanner.remove_excluded_directory("custom_exclude")
        
        self.create_file("main.tf", "resource 'aws_instance' 'web' {}")
        self.create_file("custom_exclude/main.tf", "not_excluded")
        
        result = self.scanner.scan_all(self.test_dir)
        
        self.assertEqual(result.total_files, 2)

    def test_scan_single_language(self):
        """Test scanning for single language"""
        self.create_file("main.tf", "resource 'aws_instance' 'web' {}")
        self.create_file("main.bicep", "resource storage 'Microsoft.Storage/storageAccounts@2021-04-01' = {}")
        
        result = self.scanner.scan_single_language(self.test_dir, IaCLanguage.TERRAFORM)
        
        self.assertEqual(result.total_files, 1)
        self.assertTrue(result.has_files('Terraform'))
        self.assertFalse(result.has_files('Bicep'))

    def test_get_statistics(self):
        """Test getting scan statistics"""
        self.create_file("main.tf", "resource 'aws_instance' 'web' {}")
        self.create_file("main.bicep", "resource storage 'Microsoft.Storage/storageAccounts@2021-04-01' = {}")
        
        result = self.scanner.scan_all(self.test_dir)
        stats = self.scanner.get_statistics(result)
        
        self.assertEqual(stats['total_files'], 2)
        self.assertEqual(len(stats['languages_found']), 2)
        self.assertEqual(stats['files_by_language']['Terraform'], 1)
        self.assertEqual(stats['files_by_language']['Bicep'], 1)

    def test_scan_result_properties(self):
        """Test ScanResult properties"""
        self.create_file("main.tf", "")
        self.create_file("vars.tf", "")
        
        result = self.scanner.scan_all(self.test_dir)
        
        self.assertEqual(result.total_iac_files, 2)
        self.assertIn('Terraform', result.supported_languages)

    def test_scan_nonexistent_directory(self):
        """Test scanning nonexistent directory"""
        with self.assertRaises(FileNotFoundError):
            self.scanner.scan_all("/nonexistent/directory")

    def test_scan_not_a_directory(self):
        """Test scanning a file instead of directory"""
        file_path = self.create_file("test.txt", "content")
        
        with self.assertRaises(NotADirectoryError):
            self.scanner.scan_all(str(file_path))

    def test_files_by_type(self):
        """Test files organized by extension"""
        self.create_file("main.tf", "")
        self.create_file("vars.tf", "")
        self.create_file("main.bicep", "")
        
        result = self.scanner.scan_all(self.test_dir)
        
        self.assertIn('.tf', result.files_by_type)
        self.assertIn('.bicep', result.files_by_type)
        self.assertEqual(len(result.files_by_type['.tf']), 2)
        self.assertEqual(len(result.files_by_type['.bicep']), 1)


class TestScannerFactory(unittest.TestCase):
    """Test scanner factory"""

    def test_factory_creates_default_scanner(self):
        """Test factory creates default scanner"""
        factory = ScannerFactory()
        scanner = factory.create_default_scanner()
        
        self.assertIsInstance(scanner, DirectoryScanner)

    def test_factory_creates_custom_scanner(self):
        """Test factory creates custom configured scanner"""
        factory = ScannerFactory()
        scanner = factory.create_custom_scanner(
            enabled_languages=[IaCLanguage.TERRAFORM]
        )
        
        self.assertIsInstance(scanner, DirectoryScanner)
        enabled = scanner.registry.get_enabled_languages()
        names = [config.name for config in enabled]
        
        self.assertIn('Terraform', names)
        self.assertNotIn('Bicep', names)

    def test_factory_get_registry(self):
        """Test getting registry from factory"""
        factory = ScannerFactory()
        registry = factory.get_registry()
        
        self.assertIsInstance(registry, LanguageRegistry)

    def test_convenience_function(self):
        """Test convenience create_scanner function"""
        scanner = create_scanner()
        
        self.assertIsInstance(scanner, DirectoryScanner)


class TestLanguageConfiguration(unittest.TestCase):
    """Test language configuration"""

    def test_language_config_creation(self):
        """Test creating language configuration"""
        config = LanguageConfig(
            name="Test",
            language=IaCLanguage.TERRAFORM,
            file_extensions=[".test"],
            description="Test language"
        )
        
        self.assertEqual(config.name, "Test")
        self.assertEqual(config.file_extensions, [".test"])
        self.assertTrue(config.enabled)

    def test_language_config_extensions_pattern(self):
        """Test getting extension pattern"""
        config = LanguageConfig(
            name="Multi",
            language=IaCLanguage.CLOUDFORMATION,
            file_extensions=[".yaml", ".yml", ".json"],
            description="Multiple extensions"
        )
        
        pattern = config.get_extensions_pattern()
        self.assertIn("yaml", pattern)
        self.assertIn("yml", pattern)
        self.assertIn("json", pattern)


class TestScannerIntegration(unittest.TestCase):
    """Integration tests for scanner with parsers"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.scanner = DirectoryScanner()

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def create_file(self, filename, content=""):
        """Helper to create test files"""
        filepath = Path(self.test_dir) / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content)
        return filepath

    def test_scan_for_unified_parser(self):
        """Test scanner output suitable for unified parser"""
        # Create mixed infrastructure
        self.create_file("terraform/main.tf", "resource 'aws_instance' 'web' {}")
        self.create_file("terraform/vpc.tf", "resource 'aws_vpc' 'main' {}")
        self.create_file("bicep/storage.bicep", "resource storage 'Microsoft.Storage/storageAccounts@2021-04-01' = {}")
        
        result = self.scanner.scan_all(self.test_dir)
        
        # Verify structure is suitable for unified parser
        self.assertEqual(len(result.supported_languages), 2)
        
        tf_files = result.get_files_by_language('Terraform')
        bicep_files = result.get_files_by_language('Bicep')
        
        self.assertEqual(len(tf_files), 2)
        self.assertEqual(len(bicep_files), 1)

    def test_large_directory_scan(self):
        """Test scanning large directory structure"""
        # Create a moderately large structure
        for i in range(10):
            self.create_file(f"tf_module_{i}/main.tf", "resource 'aws_instance' 'web' {}")
            self.create_file(f"bicep_module_{i}/main.bicep", "resource storage 'Microsoft.Storage/storageAccounts@2021-04-01' = {}")
        
        result = self.scanner.scan_all(self.test_dir)
        
        self.assertEqual(result.total_files, 20)
        self.assertEqual(len(result.get_files_by_language('Terraform')), 10)
        self.assertEqual(len(result.get_files_by_language('Bicep')), 10)


def run_scanner_tests():
    """Run all scanner tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestLanguageRegistry))
    suite.addTests(loader.loadTestsFromTestCase(TestDirectoryScanner))
    suite.addTests(loader.loadTestsFromTestCase(TestScannerFactory))
    suite.addTests(loader.loadTestsFromTestCase(TestLanguageConfiguration))
    suite.addTests(loader.loadTestsFromTestCase(TestScannerIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*70)
    print("UNIVERSAL SCANNER TEST SUMMARY")
    print("="*70)
    print(f"Tests Run:    {result.testsRun}")
    print(f"Successes:    {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures:     {len(result.failures)}")
    print(f"Errors:       {len(result.errors)}")
    print(f"Skipped:      {len(result.skipped)}")
    print("="*70)
    
    if result.wasSuccessful():
        print("? ALL SCANNER TESTS PASSED!")
        return 0
    else:
        print("? SOME SCANNER TESTS FAILED")
        return 1


if __name__ == '__main__':
    exit(run_scanner_tests())
