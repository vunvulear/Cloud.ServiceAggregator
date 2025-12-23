#!/usr/bin/env python3
import unittest
import tempfile
import shutil
from pathlib import Path
import sys

# Ensure src is importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from main import main as run_app

class TestOutputFolderCreation(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_output_folder_created_in_analyzed_dir(self):
        # Create a minimal Terraform file to ensure parsing finds something
        tf = Path(self.temp_dir) / 'main.tf'
        tf.write_text('resource "azurerm_storage_account" "sa" { name = "sa1" location = "eastus" }', encoding='utf-8')
        # Simulate CLI args
        sys.argv = ['main.py', self.temp_dir, '-j']
        # Run app
        exit_code = run_app()
        self.assertEqual(exit_code, 0)
        # Check output folder exists
        out_dir = Path(self.temp_dir) / 'Smart.Cloud.Aggregator.Output'
        self.assertTrue(out_dir.exists(), f"Expected output folder at {out_dir}")
        # Check report files exist
        md = out_dir / 'cloud_services_report.md'
        js = out_dir / 'cloud_services_report.json'
        self.assertTrue(md.exists(), f"Expected markdown report at {md}")
        self.assertTrue(js.exists(), f"Expected json report at {js}")

if __name__ == '__main__':
    unittest.main()