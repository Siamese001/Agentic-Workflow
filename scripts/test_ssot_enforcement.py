#!/usr/bin/env python3
"""
SSOT Enforcement Test for Dashboard End-to-End Tests
=====================================================

This test verifies that all dashboard test files use SSOT canonical definitions
instead of hardcoded column names, field names, or calculation logic.

CRITICAL: All dashboard tests MUST import and use definitions from:
- scripts/dashboard_ssot_definitions.py

This ensures:
1. No hardcoded column names (use COL_* constants)
2. No hardcoded field names (use FIELD_* constants)
3. No duplicate calculation logic (use calc_* functions)
4. Consistent naming across all test files

Usage:
  python scripts/test_ssot_enforcement.py
"""
import sys
import re
from pathlib import Path
from typing import List, Tuple

PROJECT_ROOT = Path(__file__).parent.parent

# SSOT: Import canonical definitions to verify against
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from dashboard_ssot_definitions import (
    COL_HEAL_CAP, COL_INVOCATION, COL_TEST, COL_HARDENED,
    COL_COMPLEXITY_HEALTH, COL_TYPED, COL_DOCUMENTED, COL_SCHEMA,
    COL_CANONICAL_INHERITANCE, COL_CODE_QUALITY, COL_HEALTH, COL_AVG_CC
)

# Map of hardcoded strings to their SSOT constant equivalents
SSOT_COLUMN_MAPPINGS = {
    'Heal Cap %': 'COL_HEAL_CAP',
    'Invocation %': 'COL_INVOCATION',
    'Test %': 'COL_TEST',
    'MCP Hardened %': 'COL_HARDENED',
    'Hardened %': 'COL_HARDENED',
    'Complexity Health %': 'COL_COMPLEXITY_HEALTH',
    'Complexity Health': 'COL_COMPLEXITY_HEALTH',
    'Typed %': 'COL_TYPED',
    'Documented %': 'COL_DOCUMENTED',
    'Schema Strictness %': 'COL_SCHEMA',
    'Canonical Inheritance %': 'COL_CANONICAL_INHERITANCE',
    'Code Quality Score': 'COL_CODE_QUALITY',
    'Health': 'COL_HEALTH',
    'Avg CC': 'COL_AVG_CC'
}

SSOT_FIELD_MAPPINGS = {
    'has_healing': 'FIELD_HAS_HEALING',
    'invocation': 'FIELD_INVOCATION',
    'has_tests': 'FIELD_HAS_TESTS',
    'mcp_hardened': 'FIELD_MCP_HARDENED',
    'typed_pct': 'FIELD_TYPED_PCT',
    'documented_pct': 'FIELD_DOCUMENTED_PCT',
    'schema_strictness': 'FIELD_SCHEMA_STRICTNESS',
    'proper_base_class': 'FIELD_PROPER_BASE_CLASS',
    'cyclomatic_complexity': 'FIELD_CYCLOMATIC_COMPLEXITY'
}

def check_ssot_imports(file_path: Path) -> Tuple[bool, List[str]]:
    """Check if file imports SSOT definitions."""
    errors = []
    content = file_path.read_text(encoding='utf-8')
    
    # Check for SSOT import
    has_ssot_import = 'from dashboard_ssot_definitions import' in content or \
                      'from scripts.dashboard_ssot_definitions import' in content
    
    if not has_ssot_import:
        errors.append(f"Missing SSOT import from dashboard_ssot_definitions")
        return False, errors
    
    # Check if COL_* constants are imported
    col_imports = [col for col in ['COL_HEAL_CAP', 'COL_TEST', 'COL_HEALTH'] 
                   if col in content]
    
    if len(col_imports) == 0:
        errors.append(f"No COL_* constants imported (should use SSOT column names)")
    
    return len(errors) == 0, errors

def check_hardcoded_strings(file_path: Path) -> Tuple[bool, List[str]]:
    """Check for hardcoded column/field names instead of SSOT constants."""
    errors = []
    content = file_path.read_text(encoding='utf-8')
    
    # Skip lines that are comments or imports
    lines = content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        # Skip comments and docstrings
        if line.strip().startswith('#') or line.strip().startswith('"""') or line.strip().startswith("'''"):
            continue
        
        # Check for hardcoded column names in dictionary access or string literals
        for hardcoded, ssot_const in SSOT_COLUMN_MAPPINGS.items():
            # Pattern: row['Heal Cap %'] or row.get('Heal Cap %')
            if f"['{hardcoded}']" in line or f'["{hardcoded}"]' in line or \
               f"get('{hardcoded}')" in line or f'get("{hardcoded}")' in line:
                # Check if the SSOT constant is already being used on this line
                if ssot_const not in line:
                    errors.append(
                        f"Line {line_num}: Hardcoded '{hardcoded}' should use {ssot_const}"
                    )
        
        # Check for hardcoded field names in .get() calls
        for hardcoded, ssot_const in SSOT_FIELD_MAPPINGS.items():
            if f"get('{hardcoded}')" in line or f'get("{hardcoded}")' in line:
                if ssot_const not in line:
                    errors.append(
                        f"Line {line_num}: Hardcoded '{hardcoded}' should use {ssot_const}"
                    )
    
    return len(errors) == 0, errors

def check_calculation_duplication(file_path: Path) -> Tuple[bool, List[str]]:
    """Check for duplicate calculation logic instead of SSOT functions."""
    errors = []
    content = file_path.read_text(encoding='utf-8')
    
    # Patterns that indicate duplicate calculation logic
    duplicate_patterns = [
        (r'sum\(1 for .* if .*has_healing.*\).*\*\s*100', 'calc_heal_cap_pct()'),
        (r'sum\(1 for .* if .*invocation.*\).*\*\s*100', 'calc_invocation_pct()'),
        (r'sum\(1 for .* if .*has_tests.*\).*\*\s*100', 'calc_test_pct()'),
        (r'sum\(1 for .* if .*mcp_hardened.*\).*\*\s*100', 'calc_hardened_pct()'),
    ]
    
    for pattern, ssot_func in duplicate_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            # Find line number
            line_num = content[:match.start()].count('\n') + 1
            errors.append(
                f"Line {line_num}: Duplicate calculation logic - should use {ssot_func}"
            )
    
    return len(errors) == 0, errors

def test_file_ssot_compliance(file_path: Path) -> Tuple[bool, List[str]]:
    """Test a single file for SSOT compliance."""
    all_errors = []
    
    print(f"\n{'='*70}")
    print(f"Testing: {file_path.name}")
    print(f"{'='*70}")
    
    # Test 1: SSOT imports
    passed, errors = check_ssot_imports(file_path)
    if not passed:
        all_errors.extend([f"  ❌ SSOT Import: {e}" for e in errors])
    else:
        print("  ✅ SSOT imports present")
    
    # Test 2: No hardcoded strings
    passed, errors = check_hardcoded_strings(file_path)
    if not passed:
        all_errors.extend([f"  ❌ Hardcoded String: {e}" for e in errors[:5]])  # Limit to 5
        if len(errors) > 5:
            all_errors.append(f"  ... and {len(errors) - 5} more hardcoded strings")
    else:
        print("  ✅ No hardcoded column/field names")
    
    # Test 3: No duplicate calculations
    passed, errors = check_calculation_duplication(file_path)
    if not passed:
        all_errors.extend([f"  ❌ Duplicate Calc: {e}" for e in errors])
    else:
        print("  ✅ No duplicate calculation logic")
    
    return len(all_errors) == 0, all_errors

def main():
    """Run SSOT enforcement tests on all dashboard test files."""
    print("\n" + "="*70)
    print("DASHBOARD TEST SSOT ENFORCEMENT")
    print("="*70)
    print("\nVerifying all dashboard tests use SSOT canonical definitions...")
    
    # Find all dashboard test files
    scripts_dir = PROJECT_ROOT / "scripts"
    test_files = [
        scripts_dir / "test_dashboard_end_to_end.py",
        scripts_dir / "test_dashboard_data_integrity.py",
        scripts_dir / "test_dashboard_generation.py",
    ]
    
    # Filter to existing files
    test_files = [f for f in test_files if f.exists()]
    
    if not test_files:
        print("\n❌ No dashboard test files found!")
        return 1
    
    print(f"\nFound {len(test_files)} dashboard test files to check")
    
    all_passed = True
    all_file_errors = {}
    
    for test_file in test_files:
        passed, errors = test_file_ssot_compliance(test_file)
        if not passed:
            all_passed = False
            all_file_errors[test_file.name] = errors
    
    # Summary
    print("\n" + "="*70)
    print("SSOT ENFORCEMENT SUMMARY")
    print("="*70)
    
    if all_passed:
        print("\n✅ ALL TESTS PASSED")
        print(f"\n{len(test_files)} dashboard test files comply with SSOT:")
        for test_file in test_files:
            print(f"  ✅ {test_file.name}")
        print("\n✅ SSOT ENFORCEMENT VERIFIED")
        return 0
    else:
        print(f"\n❌ {len(all_file_errors)} FILE(S) FAILED SSOT COMPLIANCE")
        for file_name, errors in all_file_errors.items():
            print(f"\n❌ {file_name}:")
            for error in errors:
                print(error)
        
        print("\n" + "="*70)
        print("FIX REQUIRED")
        print("="*70)
        print("\nAll dashboard tests MUST use SSOT canonical definitions:")
        print("  1. Import from dashboard_ssot_definitions.py")
        print("  2. Use COL_* constants for column names")
        print("  3. Use FIELD_* constants for field names")
        print("  4. Use calc_* functions for calculations")
        print("\n❌ SSOT ENFORCEMENT FAILED")
        return 1

if __name__ == '__main__':
    sys.exit(main())
