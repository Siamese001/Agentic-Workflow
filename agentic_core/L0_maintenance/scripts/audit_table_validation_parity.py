#!/usr/bin/env python3
"""
Audit validation parity between Table 1 and Table 2.
Identifies what validations exist for each table and gaps.
"""

from pathlib import Path

project_root = Path(__file__).parent.parent

print("\n" + "=" * 70)
print("TABLE VALIDATION PARITY AUDIT")
print("=" * 70)

print("\n" + "=" * 70)
print("TABLE 1 (Territory Summary) - Current Validations")
print("=" * 70)

table1_validations = [
    "✅ Sort order validation (TOTAL at top, canonical order)",
    "✅ Row count validation (24 rows expected)",
    "✅ MCP Hardening % validation (100% for all territories)",
    "✅ Data presence validation (dashboardData loaded)",
    "✅ Specific territory checks (L0, L6)",
    "✅ Exact position validation for each territory",
    "✅ Rendered in browser (Playwright)",
]

for v in table1_validations:
    print(f"  {v}")

print("\n" + "=" * 70)
print("TABLE 2 (Code Quality) - Current Validations")
print("=" * 70)

table2_validations = [
    "✅ Sort order validation (TOTAL at top, canonical order)",
    "✅ Row count validation (24 rows expected)",
    "❌ NO field value validation (Typed %, Documented %, etc.)",
    "❌ NO data presence validation for Table 2 specific fields",
    "❌ NO specific territory checks",
    "✅ Exact position validation for each territory",
    "✅ Rendered in browser (Playwright)",
]

for v in table2_validations:
    print(f"  {v}")

print("\n" + "=" * 70)
print("VALIDATION GAPS - Table 2 Missing")
print("=" * 70)

gaps = [
    "1. Field value validation",
    "   - Typed % should be 0-100",
    "   - Documented % should be 0-100",
    "   - schema Strictness % should be 0-100",
    "   - Canonical Inheritance % should be 0-100",
    "   - Code Quality Score should be 0-100",
    "",
    "2. Data integrity checks",
    "   - Verify all Table 2 fields exist in dashboardData",
    "   - Check for null/undefined values",
    "   - Validate numeric types",
    "",
    "3. Specific territory validation",
    "   - Check L0, L6 territories have correct values",
    "   - Validate TOTAL row aggregation",
    "",
    "4. Expected range warnings",
    "   - Flag territories with low Typed % (<80%)",
    "   - Flag territories with low Documented % (<70%)",
    "   - Flag territories with low Quality Score (<85%)",
]

for gap in gaps:
    print(f"  {gap}")

print("\n" + "=" * 70)
print("RECOMMENDED ENHANCEMENTS")
print("=" * 70)

recommendations = [
    "1. Add Table 2 field validation to test_mcp_hardening_all_territories.py",
    "   - Validate all Code Quality fields present",
    "   - Validate all values in range 0-100",
    "   - Check for null/undefined",
    "",
    "2. Add Table 2 data integrity to test_dashboard_data_integrity.py",
    "   - Spot-check Code Quality Score calculation",
    "   - Verify weighted formula matches SSOT",
    "",
    "3. Add Table 2 specific tests",
    "   - Validate Code Quality Score = (Typed×0.30 + Doc×0.30 + schema×0.25 + Base×0.15)",
    "   - Check TOTAL row is average/aggregate of territories",
    "",
    "4. Add deployment blocker",
    "   - Missing Table 2 fields should BLOCK deployment",
    "   - Out-of-range values should BLOCK deployment",
]

for rec in recommendations:
    print(f"  {rec}")

print("\n" + "=" * 70)
print("IMPLEMENTATION PRIORITY")
print("=" * 70)
print("\n  HIGH: Add field presence validation (deployment blocker)")
print("  HIGH: Add value range validation (deployment blocker)")
print("  MEDIUM: Add Code Quality Score calculation verification")
print("  LOW: Add expected range warnings")
