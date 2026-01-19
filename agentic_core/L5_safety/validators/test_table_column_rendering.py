#!/usr/bin/env python3
"""
Test Table Column Rendering Accuracy
=====================================

This test validates that JavaScript rendering code displays the correct
data fields in each table column. Prevents bugs like Health column showing
Code Quality Score.

CRITICAL: This test would have caught the Health/Code Quality bug.
"""
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

def test_table1_health_column_uses_correct_field():
    """Verify Table 1 Health column renders row['Health'], not Code Quality Score."""
    
    js_file = PROJECT_ROOT / "agentic_core" / "L6_observability" / "dashboards" / "js" / "renderers" / "table-renderer.js"
    js_code = js_file.read_text(encoding='utf-8')
    
    # Find renderTerritorySummaryTable function (Table 1)
    table1_start = js_code.find('function renderTerritorySummaryTable')
    table1_end = js_code.find('function renderCodeQualityTable', table1_start)
    
    if table1_start == -1:
        print("❌ FAILED: renderTerritorySummaryTable function not found")
        return False
    
    table1_code = js_code[table1_start:table1_end]
    
    # Check 1: Table 1 should NOT use Code Quality Score
    if "row['Code Quality Score']" in table1_code:
        print("❌ FAILED: Table 1 (Territory Summary) uses 'Code Quality Score' field")
        print("   This field should only be in Table 2 (Code Quality)")
        
        # Find the line
        lines = table1_code.split('\n')
        for i, line in enumerate(lines):
            if "row['Code Quality Score']" in line:
                print(f"   Line {i}: {line.strip()}")
        return False
    
    # Check 2: Table 1 MUST use Health field
    if "row['Health']" not in table1_code:
        print("❌ FAILED: Table 1 doesn't use 'Health' field")
        print("   Health column must display row['Health']")
        return False
    
    print("✅ PASSED: Table 1 Health column uses correct field (row['Health'])")
    return True

def test_table2_code_quality_column_uses_correct_field():
    """Verify Table 2 Code Quality column renders row['Code Quality Score']."""
    
    js_file = PROJECT_ROOT / "agentic_core" / "L6_observability" / "dashboards" / "js" / "renderers" / "table-renderer.js"
    js_code = js_file.read_text(encoding='utf-8')
    
    # Find renderCodeQualityTable function (Table 2)
    table2_start = js_code.find('function renderCodeQualityTable')
    
    if table2_start == -1:
        print("❌ FAILED: renderCodeQualityTable function not found")
        return False
    
    # Get rest of file from table2_start
    table2_code = js_code[table2_start:table2_start + 5000]  # Next 5000 chars
    
    # Check: Table 2 MUST use Code Quality Score
    if "row['Code Quality Score']" not in table2_code:
        print("❌ FAILED: Table 2 doesn't use 'Code Quality Score' field")
        return False
    
    print("✅ PASSED: Table 2 Code Quality column uses correct field")
    return True

def test_health_color_uses_health_field():
    """Verify healthColor variable uses row['Health'], not Code Quality Score."""
    
    js_file = PROJECT_ROOT / "agentic_core" / "L6_observability" / "dashboards" / "js" / "renderers" / "table-renderer.js"
    js_code = js_file.read_text(encoding='utf-8')
    
    # Find healthColor assignment in Table 1
    table1_start = js_code.find('function renderTerritorySummaryTable')
    table1_end = js_code.find('function renderCodeQualityTable', table1_start)
    table1_code = js_code[table1_start:table1_end]
    
    # Look for healthColor assignment
    health_color_match = re.search(r"const healthColor = getWorstCaseColor\(row\['([^']+)'\]", table1_code)
    
    if not health_color_match:
        print("❌ FAILED: healthColor assignment not found")
        return False
    
    field_used = health_color_match.group(1)
    
    if field_used != 'Health':
        print(f"❌ FAILED: healthColor uses row['{field_used}'] instead of row['Health']")
        return False
    
    print("✅ PASSED: healthColor uses correct field (row['Health'])")
    return True

def test_column_field_mapping():
    """Verify Table 1 columns use correct data fields."""
    
    js_file = PROJECT_ROOT / "agentic_core" / "L6_observability" / "dashboards" / "js" / "renderers" / "table-renderer.js"
    js_code = js_file.read_text(encoding='utf-8')
    
    # Expected column-to-field mappings for Table 1
    expected_fields = [
        'Heal Cap %',
        'Invocation %',
        'MCP Hardened %',
        'Test %',
        'Complexity Health %',
        'Health',  # ← Critical: NOT 'Code Quality Score'
    ]
    
    table1_start = js_code.find('function renderTerritorySummaryTable')
    table1_end = js_code.find('function renderCodeQualityTable', table1_start)
    table1_code = js_code[table1_start:table1_end]
    
    missing_fields = []
    for field in expected_fields:
        if f"row['{field}']" not in table1_code:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"❌ FAILED: Table 1 missing field references: {missing_fields}")
        return False
    
    print(f"✅ PASSED: All {len(expected_fields)} expected fields found in Table 1")
    return True

def main():
    """Run all table column rendering tests."""
    print("\n" + "="*70)
    print("TABLE COLUMN RENDERING VALIDATION")
    print("="*70)
    print("\nPrevents bugs where wrong data field is displayed in a column.")
    print("Example: Health column showing Code Quality Score value.\n")
    
    tests = [
        ("Table 1 Health Column Field", test_table1_health_column_uses_correct_field),
        ("Table 2 Code Quality Column Field", test_table2_code_quality_column_uses_correct_field),
        ("Health Color Variable Field", test_health_color_uses_health_field),
        ("Column-to-Field Mapping", test_column_field_mapping),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'─'*70}")
        print(f"Running: {test_name}")
        print(f"{'─'*70}")
        passed = test_func()
        results.append((test_name, passed))
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n{passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n✅ ALL COLUMN RENDERING TESTS PASSED")
        return 0
    else:
        print(f"\n❌ {total_count - passed_count} TEST(S) FAILED")
        print("\nColumn rendering has issues that could cause wrong data to display.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
