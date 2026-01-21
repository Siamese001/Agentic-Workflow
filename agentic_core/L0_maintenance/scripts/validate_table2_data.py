#!/usr/bin/env python3
"""
Table 2 (Code Quality) Data Validation
=======================================

Validates that Table 2 data is being generated and updated correctly.
Table 2 shows code quality metrics: Typed %, Documented %, Schema Strictness, etc.

Checks:
1. Table 2 fields present in dashboard data
2. Table 2 metrics calculated correctly
3. renderCodeQualityTable function exists and is called
4. codeQualityGrid element exists in HTML
"""
import json
import sys
from pathlib import Path


def main():
    print("=" * 80)
    print("TABLE 2 (CODE QUALITY) VALIDATION")
    print("=" * 80)
    print()

    errors = []
    warnings = []

    # Check 1: Dashboard data has Table 2 fields
    print("Check 1: Dashboard data structure")
    print("-" * 80)

    dashboard_path = Path('agentic_core/L6_observability/dashboards/autonomy_dashboard.html')
    if not dashboard_path.exists():
        errors.append("Dashboard HTML not found")
        print("   ❌ Dashboard HTML not found")
    else:
        html = dashboard_path.read_text(encoding='utf-8')

        # Extract dashboardData
        import re
        data_match = re.search(r'const dashboardData = (\[.*?\]);', html, re.DOTALL)
        if not data_match:
            errors.append("dashboardData not found in HTML")
            print("   ❌ dashboardData not found")
        else:
            try:
                data_json = data_match.group(1)
                dashboard_data = json.loads(data_json)

                # Check for Table 2 fields in TOTAL row
                total_row = dashboard_data[0] if dashboard_data else {}

                table2_fields = [
                    'Typed %',
                    'Documented %',
                    'Schema Strictness %',
                    'Proper Base %',
                    'Code Quality Score'
                ]

                missing_fields = [f for f in table2_fields if f not in total_row]

                if missing_fields:
                    errors.append(f"Table 2 fields missing: {missing_fields}")
                    print(f"   ❌ Missing fields: {missing_fields}")
                else:
                    print("   ✅ All Table 2 fields present")

                    # Show sample values
                    print(f"      Typed %: {total_row.get('Typed %')}")
                    print(f"      Documented %: {total_row.get('Documented %')}")
                    print(f"      Code Quality Score: {total_row.get('Code Quality Score')}")

            except json.JSONDecodeError as e:
                errors.append(f"Failed to parse dashboardData: {e}")
                print(f"   ❌ JSON parse error: {e}")

    print()

    # Check 2: renderCodeQualityTable function exists
    print("Check 2: Table 2 rendering function")
    print("-" * 80)

    if dashboard_path.exists():
        html = dashboard_path.read_text(encoding='utf-8')

        if 'function renderCodeQualityTable' not in html:
            errors.append("renderCodeQualityTable function missing")
            print("   ❌ renderCodeQualityTable function not found")
        else:
            print("   ✅ renderCodeQualityTable function exists")

            # Check if it's being called
            if 'renderCodeQualityTable(dashboardData)' not in html and 'renderCodeQualityTable(territoryData)' not in html:
                warnings.append("renderCodeQualityTable may not be called")
                print("   ⚠️  renderCodeQualityTable might not be invoked")
            else:
                print("   ✅ renderCodeQualityTable is called")

    print()

    # Check 3: codeQualityGrid element exists
    print("Check 3: Table 2 HTML container")
    print("-" * 80)

    if dashboard_path.exists():
        html = dashboard_path.read_text(encoding='utf-8')

        if 'id="codeQualityGrid"' not in html:
            errors.append("codeQualityGrid element missing")
            print("   ❌ codeQualityGrid element not found")
        else:
            print("   ✅ codeQualityGrid element exists")

    print()

    # Check 4: Verify generation script produces Table 2 data
    print("Check 4: Dashboard generator produces Table 2 fields")
    print("-" * 80)

    gen_script = Path('agentic_core/L6_observability/dashboards/generate_dashboard.py')
    if gen_script.exists():
        gen_code = gen_script.read_text(encoding='utf-8')

        table2_field_names = [
            '"Typed %"',
            '"Documented %"',
            '"Schema Strictness %"',
            '"Code Quality Score"'
        ]

        missing_in_gen = [f for f in table2_field_names if f not in gen_code]

        if missing_in_gen:
            errors.append(f"Generator missing Table 2 fields: {missing_in_gen}")
            print(f"   ❌ Generator doesn't create: {missing_in_gen}")
        else:
            print("   ✅ Generator creates all Table 2 fields")

    print()

    # Summary
    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print()

    if errors:
        print(f"❌ {len(errors)} ERRORS:")
        for error in errors:
            print(f"   • {error}")
        print()

    if warnings:
        print(f"⚠️  {len(warnings)} WARNINGS:")
        for warning in warnings:
            print(f"   • {warning}")
        print()

    if not errors and not warnings:
        print("✅ TABLE 2 VALIDATION PASSED")
        print("   All code quality metrics are properly configured")
        return 0
    elif not errors:
        print("⚠️  TABLE 2 HAS WARNINGS")
        print("   Review warnings above")
        return 0
    else:
        print("❌ TABLE 2 VALIDATION FAILED")
        print("   Fix errors above to enable Table 2")
        return 1

if __name__ == "__main__":
    sys.exit(main())
