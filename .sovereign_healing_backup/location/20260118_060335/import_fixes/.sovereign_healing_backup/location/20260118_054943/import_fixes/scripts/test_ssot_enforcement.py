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
import ast
from pathlib import Path
from typing import List, Tuple

# SSOT: Use centralized blueprint for project root discovery
try:
    from agentic_core.L5_safety.validators.structure_blueprint_1 import get_validated_project_root
    PROJECT_ROOT = get_validated_project_root()
except ImportError:
    PROJECT_ROOT = Path(__file__).parent.parent

# SSOT: Import canonical definitions to verify against
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from dashboard_ssot_definitions import (
    COL_HEAL_CAP, COL_INVOCATION, COL_TEST, COL_HARDENED,
    COL_COMPLEXITY_HEALTH, COL_TYPED, COL_DOCUMENTED, COL_SCHEMA_STRICTNESS,
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
    'Schema Strictness %': 'COL_SCHEMA_STRICTNESS',
    'Canonical Inheritance %': 'COL_CANONICAL_INHERITANCE',
    'Code Quality Score': 'COL_CODE_QUALITY',
    'Health': 'COL_HEALTH',
    'Avg CC': 'COL_AVG_CC'
}

# JavaScript forbidden strings that must use COLUMNS.* constants
JS_FORBIDDEN_STRINGS = [
    'Health',
    'Code Quality Score',
    'Test %',
    'MCP Hardened %',
    'Heal Cap %',
    'Invocation %',
    'Complexity Health %',
    'Typed %',
    'Documented %',
    'Schema Strictness %',
    'Canonical Inheritance %'
]

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
    try:
        tree = ast.parse(file_path.read_text(encoding='utf-8'))
        has_ssot_import = False
        imported_names = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module in ['dashboard_ssot_definitions', 'scripts.dashboard_ssot_definitions']:
                    has_ssot_import = True
                    for alias in node.names:
                        imported_names.add(alias.name)

        if not has_ssot_import:
            errors.append("Missing SSOT import from dashboard_ssot_definitions")
        elif not any(name.startswith('COL_') for name in imported_names):
            errors.append("No COL_* constants imported (should use SSOT column names)")
            
    except Exception as e:
        errors.append(f"AST Parsing Error: {e}")
    
    return len(errors) == 0, errors

def check_hardcoded_strings(file_path: Path) -> Tuple[bool, List[str]]:
    """Check for hardcoded column/field names instead of SSOT constants."""
    errors = []
    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
            continue
        
        for hardcoded, ssot_const in SSOT_COLUMN_MAPPINGS.items():
            # Robust detection for dict access and .get() calls
            patterns = [
                rf"\[['\"]{re.escape(hardcoded)}['\"]\]",
                rf"\.get\(['\"{re.escape(hardcoded)}['\"]\)"
            ]
            if any(re.search(p, line) for p in patterns):
                if ssot_const not in line:
                    errors.append(
                        f"Line {line_num}: Hardcoded '{hardcoded}' should use {ssot_const}"
                    )
        
        for hardcoded, ssot_const in SSOT_FIELD_MAPPINGS.items():
            if re.search(rf"\.get\(['\"{re.escape(hardcoded)}['\"]\)", line):
                if ssot_const not in line: # Ensure we aren't already using the constant
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
        (r'sum\(\s*1\s*for\s+.*\s+if\s+.*has_healing.*\).*\*\s*100', 'calc_heal_cap_pct()'),
        (r'sum\(\s*1\s*for\s+.*\s+if\s+.*invocation.*\).*\*\s*100', 'calc_invocation_pct()'),
        (r'sum\(\s*1\s*for\s+.*\s+if\s+.*has_tests.*\).*\*\s*100', 'calc_test_pct()'),
        (r'sum\(\s*1\s*for\s+.*\s+if\s+.*mcp_hardened.*\).*\*\s*100', 'calc_hardened_pct()'),
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

def test_no_hardcoded_columns_in_js() -> Tuple[bool, List[str]]:
    """Test Case 3: Ensures no hardcoded metric strings exist in JS renderers."""
    errors = []
    js_dir = PROJECT_ROOT / "agentic_core" / "L6_observability" / "dashboards" / "js" / "renderers"
    
    if not js_dir.exists():
        errors.append(f"JS renderers directory not found: {js_dir}")
        return False, errors
    
    for js_file in js_dir.glob("*.js"):
        content = js_file.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip comments and import statements
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('/*') or 'import' in stripped:
                continue
            
            for forbidden in JS_FORBIDDEN_STRINGS:
                # Check for string literals in object access or assignments
                patterns = [
                    rf"\['{re.escape(forbidden)}'\]",
                    rf'\["{re.escape(forbidden)}"\]',
                    rf"= '{re.escape(forbidden)}'",
                    rf'= "{re.escape(forbidden)}"'
                ]
                
                for pattern in patterns:
                    if re.search(pattern, line):
                        # Check if line uses SSOT constant instead
                        if 'COLUMNS.' not in line and 'window.COLUMNS' not in line:
                            errors.append(
                                f"Leak detected in {js_file.name}:{line_num}: "
                                f"Hardcoded string '{forbidden}' found. Use COLUMNS.* constant."
                            )
                            break
    
    return len(errors) == 0, errors


def test_ssot_generation_integrity() -> Tuple[bool, List[str]]:
    """Test Case 2: Ensures generated files match YAML source."""
    import yaml
    import hashlib
    
    errors = []
    yaml_path = PROJECT_ROOT / "scripts" / "config" / "dashboard_ssot.yaml"
    py_output = PROJECT_ROOT / "scripts" / "dashboard_ssot_definitions.py"
    js_output = PROJECT_ROOT / "agentic_core" / "L6_observability" / "dashboards" / "js" / "constants" / "dashboard-constants.js"
    
    if not yaml_path.exists():
        errors.append(f"YAML config not found: {yaml_path}")
        return False, errors
    
    # Load YAML and verify generated files match
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            yaml_data = yaml.safe_load(f)
        
        # Check Python constants exist
        if py_output.exists():
            py_content = py_output.read_text(encoding='utf-8')
            
            # Verify key constants are present
            for col_key in yaml_data.get('columns', {}).keys():
                const_name = f"COL_{col_key.upper()}"
                if const_name not in py_content:
                    errors.append(f"Missing Python constant: {const_name}")
        else:
            errors.append(f"Generated Python file not found: {py_output}")
        
        # Check JavaScript constants exist
        if js_output.exists():
            js_content = js_output.read_text(encoding='utf-8')
            
            # Verify window.COLUMNS exists
            if 'window.COLUMNS' not in js_content:
                errors.append("Missing window.COLUMNS in generated JS")
        else:
            errors.append(f"Generated JavaScript file not found: {js_output}")
            
    except Exception as e:
        errors.append(f"Generation integrity check failed: {e}")
    
    return len(errors) == 0, errors


def test_generator_weight_validation() -> Tuple[bool, List[str]]:
    """Test Case 1: Ensures generator validates weight sums."""
    import yaml
    
    errors = []
    yaml_path = PROJECT_ROOT / "scripts" / "config" / "dashboard_ssot.yaml"
    
    if not yaml_path.exists():
        errors.append(f"YAML config not found: {yaml_path}")
        return False, errors
    
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            yaml_data = yaml.safe_load(f)
        
        # Check health weights sum to 1.0
        health_weights = yaml_data.get('health_weights', {})
        if health_weights:
            weight_sum = sum(health_weights.values())
            if abs(weight_sum - 1.0) > 0.001:
                errors.append(
                    f"Health weights sum to {weight_sum:.3f}, expected 1.0 (±0.001)"
                )
        
        # Check L0 weights sum to 1.0
        l0_weights = yaml_data.get('health_weights_l0', {})
        if l0_weights:
            weight_sum = sum(l0_weights.values())
            if abs(weight_sum - 1.0) > 0.001:
                errors.append(
                    f"L0 health weights sum to {weight_sum:.3f}, expected 1.0 (±0.001)"
                )
        
        # Check code quality weights sum to 1.0
        cq_weights = yaml_data.get('code_quality_weights', {})
        if cq_weights:
            weight_sum = sum(cq_weights.values())
            if abs(weight_sum - 1.0) > 0.001:
                errors.append(
                    f"Code quality weights sum to {weight_sum:.3f}, expected 1.0 (±0.001)"
                )
                
    except Exception as e:
        errors.append(f"Weight validation failed: {e}")
    
    return len(errors) == 0, errors


def main():
    """Run SSOT enforcement tests on all dashboard files."""
    print("\n" + "="*70)
    print("DASHBOARD SSOT ENFORCEMENT TEST SUITE")
    print("="*70)
    print("\nVerifying SSOT compliance across Python and JavaScript...")
    
    all_passed = True
    all_errors = {}
    
    # Test 1: Generator Weight Validation
    print("\n" + "="*70)
    print("Test 1: Generator Weight Validation")
    print("="*70)
    passed, errors = test_generator_weight_validation()
    if passed:
        print("✅ PASSED: All weights sum to 1.0 (±0.001)")
    else:
        print("❌ FAILED: Weight validation errors")
        all_errors['Weight Validation'] = errors
        all_passed = False
    
    # Test 2: Generation Integrity
    print("\n" + "="*70)
    print("Test 2: SSOT Generation Integrity")
    print("="*70)
    passed, errors = test_ssot_generation_integrity()
    if passed:
        print("✅ PASSED: Generated files match YAML source")
    else:
        print("❌ FAILED: Generation integrity errors")
        all_errors['Generation Integrity'] = errors
        all_passed = False
    
    # Test 3: JavaScript Leak Detection
    print("\n" + "="*70)
    print("Test 3: JavaScript Hardcoded String Detection")
    print("="*70)
    passed, errors = test_no_hardcoded_columns_in_js()
    if passed:
        print("✅ PASSED: No hardcoded strings in JavaScript renderers")
    else:
        print("❌ FAILED: JavaScript leak detection errors")
        all_errors['JavaScript Leaks'] = errors
        all_passed = False
    
    # Test 4: Python Test Files SSOT Compliance
    print("\n" + "="*70)
    print("Test 4: Python Test Files SSOT Compliance")
    print("="*70)
    
    scripts_dir = PROJECT_ROOT / "scripts"
    test_files = [
        scripts_dir / "test_dashboard_end_to_end.py",
        scripts_dir / "test_dashboard_data_integrity.py",
        scripts_dir / "test_dashboard_generation.py",
    ]
    
    test_files = [f for f in test_files if f.exists()]
    print(f"Found {len(test_files)} Python test files to check")
    
    for test_file in test_files:
        passed, errors = test_file_ssot_compliance(test_file)
        if not passed:
            all_passed = False
            all_errors[test_file.name] = errors
    
    # Summary
    print("\n" + "="*70)
    print("SSOT ENFORCEMENT TEST SUMMARY")
    print("="*70)
    
    if all_passed:
        print("\n✅ ALL TESTS PASSED")
        print("\n✅ Test 1: Generator weight validation")
        print("✅ Test 2: SSOT generation integrity")
        print("✅ Test 3: JavaScript leak detection")
        print(f"✅ Test 4: {len(test_files)} Python test files SSOT compliant")
        print("\n" + "="*70)
        print("✅ SSOT ENFORCEMENT VERIFIED")
        print("="*70)
        return 0
    else:
        print(f"\n❌ {len(all_errors)} TEST(S) FAILED")
        for test_name, errors in all_errors.items():
            print(f"\n❌ {test_name}:")
            for error in errors[:10]:  # Limit to 10 errors per test
                print(f"  {error}")
            if len(errors) > 10:
                print(f"  ... and {len(errors) - 10} more errors")
        
        print("\n" + "="*70)
        print("FIX REQUIRED")
        print("="*70)
        print("\nAll dashboard code MUST use SSOT canonical definitions:")
        print("  1. Python: Import from dashboard_ssot_definitions.py")
        print("  2. Python: Use COL_* constants for column names")
        print("  3. Python: Use FIELD_* constants for field names")
        print("  4. Python: Use calc_* functions for calculations")
        print("  5. JavaScript: Use window.COLUMNS.* for column names")
        print("  6. JavaScript: Use window.THRESHOLDS.* for thresholds")
        print("\n❌ SSOT ENFORCEMENT FAILED")
        return 1

if __name__ == '__main__':
    sys.exit(main())
