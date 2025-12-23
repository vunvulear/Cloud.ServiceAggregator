#!/usr/bin/env python3
"""
Test script for Smart Cloud Aggregator
Verifies the tool works correctly with sample data
"""

import subprocess
import sys
import os
import json
from pathlib import Path


def run_test(test_name, command, expect_success=True):
    """Run a test and report results"""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")
    print(f"Command: {command}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if expect_success:
        if result.returncode == 0:
            print("? PASSED")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print("? FAILED")
            print("STDERR:", result.stderr)
            return False
    else:
        if result.returncode != 0:
            print("? PASSED (expected failure)")
            return True
        else:
            print("? FAILED (expected to fail)")
            return False


def verify_outputs():
    """Verify generated files"""
    print(f"\n{'='*60}")
    print("VERIFYING OUTPUTS")
    print(f"{'='*60}")
    
    tests_passed = 0
    tests_total = 0
    
    # Check markdown file
    tests_total += 1
    if Path("test_report.md").exists():
        with open("test_report.md") as f:
            content = f.read()
            if "# Azure Services Assessment Report" in content and len(content) > 100:
                print("? Markdown report generated correctly")
                tests_passed += 1
            else:
                print("? Markdown report is invalid or empty")
    else:
        print("? Markdown report not found")
    
    # Check JSON file
    tests_total += 1
    if Path("test_report.json").exists():
        try:
            with open("test_report.json") as f:
                data = json.load(f)
                if isinstance(data, dict) and len(data) > 0:
                    print("? JSON report generated correctly")
                    tests_passed += 1
                else:
                    print("? JSON report is empty")
        except json.JSONDecodeError:
            print("? JSON report is invalid")
    else:
        print("? JSON report not found")
    
    return tests_passed, tests_total


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("SMART CLOUD AGGREGATOR - TEST SUITE")
    print("="*60)
    
    # Change to parent directory (project root)
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Basic analysis
    tests_total += 1
    if run_test(
        "Basic Analysis",
        "python main.py ./examples -o test_report.md -j"
    ):
        tests_passed += 1
    
    # Verify outputs
    verify_passed, verify_total = verify_outputs()
    tests_passed += verify_passed
    tests_total += verify_total
    
    # Test 2: Verbose mode
    tests_total += 1
    if run_test(
        "Verbose Mode",
        "python main.py ./examples -v -o verbose_test.md"
    ):
        tests_passed += 1
    
    # Test 3: Non-existent directory (should fail)
    tests_total += 1
    if run_test(
        "Invalid Path (Expected Failure)",
        "python main.py ./nonexistent",
        expect_success=False
    ):
        tests_passed += 1
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests Passed: {tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print("\n? ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n? {tests_total - tests_passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
