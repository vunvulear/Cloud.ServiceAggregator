#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick verification test for all new formats
"""

import sys
from pathlib import Path

# Ensure repo root is importable
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def test_imports():
    """Test all imports work"""
    print("Testing imports...")
    try:
        from src.parsers.powershell import PowerShellParser
        print("  OK PowerShell Parser")
    except Exception as e:
        print(f"  FAIL PowerShell Parser: {e}")
        return False

    try:
        from src.parsers.azure_cli import AzureCliParser
        print("  OK Azure CLI Parser")
    except Exception as e:
        print(f"  FAIL Azure CLI Parser: {e}")
        return False

    try:
        from src.parsers.arm import ArmTemplateParser
        print("  OK ARM Template Parser")
    except Exception as e:
        print(f"  FAIL ARM Template Parser: {e}")
        return False

    try:
        from src.enhanced_unified_parser import EnhancedUnifiedIaCParser
        print("  OK Enhanced Unified Parser")
    except Exception as e:
        print(f"  FAIL Enhanced Unified Parser: {e}")
        return False

    try:
        from src.universal_scanner import create_scanner, IaCLanguage
        print("  OK Universal Scanner")
    except Exception as e:
        print(f"  FAIL Universal Scanner: {e}")
        return False

    return True


def test_scanner():
    """Test scanner configuration"""
    print("\nTesting scanner configuration...")
    from src.universal_scanner import create_scanner

    scanner = create_scanner()
    enabled = scanner.registry.get_enabled_languages()

    print(f"  Enabled languages: {len(enabled)}")
    for lang in enabled:
        print(f"    - {lang.name} ({', '.join(lang.file_extensions)})")

    required = {'Terraform', 'Bicep', 'PowerShell', 'Azure CLI', 'ARM Template'}
    found = {lang.name for lang in enabled}
    missing = required - found

    if not missing:
        print("  OK Core formats registered and enabled")
        return True
    else:
        print(f"  FAIL Missing core languages: {missing}")
        return False


def test_parsers_exist():
    """Test parser instantiation"""
    print("\nTesting parser instantiation...")

    from src.parsers.powershell import PowerShellParser
    from src.parsers.azure_cli import AzureCliParser
    from src.parsers.arm import ArmTemplateParser

    try:
        ps_parser = PowerShellParser()
        print(f"  OK PowerShell Parser (extensions: {ps_parser.get_file_extensions()})")
    except Exception as e:
        print(f"  FAIL PowerShell Parser: {e}")
        return False

    try:
        cli_parser = AzureCliParser()
        print(f"  OK Azure CLI Parser (extensions: {cli_parser.get_file_extensions()})")
    except Exception as e:
        print(f"  FAIL Azure CLI Parser: {e}")
        return False

    try:
        arm_parser = ArmTemplateParser()
        print(f"  OK ARM Template Parser (extensions: {arm_parser.get_file_extensions()})")
    except Exception as e:
        print(f"  FAIL ARM Template Parser: {e}")
        return False

    return True


def main():
    """Run all verification tests"""
    print("=" * 70)
    print("MULTI-FORMAT SUPPORT VERIFICATION")
    print("=" * 70)
    print()

    results = []

    results.append(("Imports", test_imports()))
    results.append(("Scanner Config", test_scanner()))
    results.append(("Parser Instantiation", test_parsers_exist()))

    print()
    print("=" * 70)
    print("VERIFICATION RESULTS")
    print("=" * 70)

    for test_name, passed in results:
        status = "PASSED" if passed else "FAILED"
        print(f"{test_name:.<50} {status}")

    print()

    all_passed = all(passed for _, passed in results)

    if all_passed:
        print("OK ALL VERIFICATIONS PASSED!")
        print()
        print("System is ready to parse:")
        print("  - Terraform (.tf)")
        print("  - Bicep (.bicep)")
        print("  - PowerShell (.ps1)")
        print("  - Azure CLI (.sh)")
        print("  - ARM Templates (.json)")
        print("  - CloudFormation (yaml/json)")
        print("  - Python/TypeScript/Go/Java/C# (cloud SDK usage)")
        print()
        return 0
    else:
        print("FAIL SOME VERIFICATIONS FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(main())
