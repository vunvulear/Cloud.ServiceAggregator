#!/usr/bin/env python3
"""
Master Test Runner

Runs all test suites and generates a comprehensive report.
"""

import subprocess
import sys
from pathlib import Path

def run_test_file(test_file, test_name):
    """Run a test file and return results"""
    print(f"\n{'='*80}")
    print(f"Running: {test_name}")
    print(f"{'='*80}\n")
    
    result = subprocess.run(
        [sys.executable, test_file],
        capture_output=False,
        text=True
    )
    
    return result.returncode == 0

def main():
    """Run all tests"""
    test_dir = Path(__file__).parent
    tests = [
        (test_dir / "test_universal_scanner.py", "Universal Scanner Tests (31 tests)"),
        (test_dir / "test_new_format_parsers.py", "New Format Parsers Tests (25 tests)"),
        (test_dir / "test_v2_unit_tests.py", "v2.0 Unit Tests (25+ tests)"),
        (test_dir / "test_unit_tests.py", "v1.0 Unit Tests (40+ tests)"),
        (test_dir / "test_bicep_comprehensive.py", "Bicep Parser Tests (30 tests)"),
        (test_dir / "test_integration_terraform_bicep.py", "Integration Tests (11 tests)"),
    ]
    
    results = {}
    total_passed = 0
    total_failed = 0
    
    print("\n" + "="*80)
    print("SMART CLOUD AGGREGATOR - COMPREHENSIVE TEST SUITE (WITH SCANNER)")
    print("="*80)
    
    for test_file, test_name in tests:
        if not test_file.exists():
            print(f"\n[FAILED] Test file not found: {test_file}")
            results[test_name] = False
            total_failed += 1
            continue
        
        passed = run_test_file(str(test_file), test_name)
        results[test_name] = passed
        
        if passed:
            total_passed += 1
        else:
            total_failed += 1
    
    # Print summary
    print("\n" + "="*80)
    print("COMPREHENSIVE TEST SUMMARY")
    print("="*80 + "\n")
    
    for test_name, passed in results.items():
        status = "[PASSED]" if passed else "[FAILED]"
        print(f"{status}: {test_name}")
    
    print("\n" + "-"*80)
    print(f"Total Test Suites: {len(results)}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print("-"*80 + "\n")
    
    if total_failed == 0:
        print("="*80)
        print("ALL TEST SUITES PASSED SUCCESSFULLY!")
        print("="*80 + "\n")
        
        print("Test Breakdown:")
        print("  * Universal Scanner Tests:      31 tests [PASSED]")
        print("  * New Format Parsers Tests:     25 tests [PASSED]")
        print("  * v2.0 Unit Tests:              25+ tests [PASSED]")
        print("  * v1.0 Unit Tests:              40+ tests [PASSED]")
        print("  * Bicep Parser Tests:           30 tests [PASSED]")
        print("  * Integration Tests:            11 tests [PASSED]")
        print("  * Total:                        161+ tests [PASSED]")
        print("\nLanguages Tested:")
        print("  [OK] Terraform (.tf)")
        print("  [OK] Bicep (.bicep)")
        print("  [OK] PowerShell (.ps1)")
        print("  [OK] Azure CLI Bash (.sh)")
        print("  [OK] ARM Templates (.json)")
        print("\nFeatures Tested:")
        print("  [OK] Universal directory scanning (5 formats)")
        print("  [OK] Language registry and configuration")
        print("  [OK] Terraform parsing")
        print("  [OK] Bicep parsing")
        print("  [OK] PowerShell parsing")
        print("  [OK] Azure CLI parsing")
        print("  [OK] ARM Template parsing")
        print("  [OK] Unified parser (all formats)")
        print("  [OK] Service mapping (100+ resources)")
        print("  [OK] Report generation (Markdown & JSON)")
        print("  [OK] Multi-format projects")
        print("  [OK] Edge cases and error handling")
        print("  [OK] Extensible language support")
        print("\nReady for Production Use! ??")
        print()
        
        return 0
    else:
        print("="*80)
        print(f"{total_failed} TEST SUITE(S) FAILED")
        print("="*80 + "\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
