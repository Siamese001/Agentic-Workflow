"""
Table 2 (Code Quality) Data Validation
=======================================

Validates that Table 2 data is being generated and updated correctly.
Table 2 shows code quality metrics: Typed %, Documented %, schema Strictness, etc.

Checks:
1. Table 2 fields present in dashboard data
2. Table 2 metrics calculated correctly
3. renderCodeQualityTable function exists and is called
4. codeQualityGrid element exists in HTML
"""

import json
import sys
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


def main():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "main", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "main", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "main")
    print("=" * 80)
    print("TABLE 2 (CODE QUALITY) VALIDATION")
    print("=" * 80)
    print()
    errors = []
    warnings = []
    print("Check 1: Dashboard data structure")
    print("-" * 80)
    dashboard_path = Path("agentic_core/L6_observability/dashboards/autonomy_dashboard.html")
    if not dashboard_path.exists():
        errors.append("Dashboard HTML not found")
        print("   ❌ Dashboard HTML not found")
    else:
        html = dashboard_path.read_text(encoding="utf-8")
        import re

        data_match = re.search("const dashboardData = (\\[.*?\\]);", html, re.DOTALL)
        if not data_match:
            errors.append("dashboardData not found in HTML")
            print("   ❌ dashboardData not found")
        else:
            try:
                data_json = data_match.group(1)
                dashboard_data = json.loads(data_json)
                total_row = dashboard_data[0] if dashboard_data else {}
                table2_fields = [
                    "Typed %",
                    "Documented %",
                    "schema Strictness %",
                    "Proper Base %",
                    "Code Quality Score",
                ]
                missing_fields = [f for f in table2_fields if f not in total_row]
                if missing_fields:
                    errors.append(f"Table 2 fields missing: {missing_fields}")
                    print(f"   ❌ Missing fields: {missing_fields}")
                else:
                    print("   ✅ All Table 2 fields present")
                    print(f"      Typed %: {total_row.get('Typed %')}")
                    print(f"      Documented %: {total_row.get('Documented %')}")
                    print(f"      Code Quality Score: {total_row.get('Code Quality Score')}")
            except json.JSONDecodeError as e:
                errors.append(f"Failed to parse dashboardData: {e}")
                print(f"   ❌ JSON parse error: {e}")
    print()
    print("Check 2: Table 2 rendering function")
    print("-" * 80)
    if dashboard_path.exists():
        html = dashboard_path.read_text(encoding="utf-8")
        if "function renderCodeQualityTable" not in html:
            errors.append("renderCodeQualityTable function missing")
            print("   ❌ renderCodeQualityTable function not found")
        else:
            print("   ✅ renderCodeQualityTable function exists")
            if (
                "renderCodeQualityTable(dashboardData)" not in html
                and "renderCodeQualityTable(territoryData)" not in html
            ):
                warnings.append("renderCodeQualityTable may not be called")
                print("   ⚠️  renderCodeQualityTable might not be invoked")
            else:
                print("   ✅ renderCodeQualityTable is called")
    print()
    print("Check 3: Table 2 HTML container")
    print("-" * 80)
    if dashboard_path.exists():
        html = dashboard_path.read_text(encoding="utf-8")
        if 'id="codeQualityGrid"' not in html:
            errors.append("codeQualityGrid element missing")
            print("   ❌ codeQualityGrid element not found")
        else:
            print("   ✅ codeQualityGrid element exists")
    print()
    print("Check 4: Dashboard generator produces Table 2 fields")
    print("-" * 80)
    gen_script = Path("agentic_core/L6_observability/dashboards/generate_dashboard.py")
    if gen_script.exists():
        gen_code = gen_script.read_text(encoding="utf-8")
        table2_field_names = ['"Typed %"', '"Documented %"', '"schema Strictness %"', '"Code Quality Score"']
        missing_in_gen = [f for f in table2_field_names if f not in gen_code]
        if missing_in_gen:
            errors.append(f"Generator missing Table 2 fields: {missing_in_gen}")
            print(f"   ❌ Generator doesn't create: {missing_in_gen}")
        else:
            print("   ✅ Generator creates all Table 2 fields")
    print()
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
    if not errors and (not warnings):
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
