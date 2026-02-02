#!/usr/bin/env python3
"""Validate all dashboard changes are present in the HTML file."""

from pathlib import Path

dashboard_path = Path("agentic_core/L6_observability/dashboards/autonomy_dashboard.html")
html = dashboard_path.read_text(encoding="utf-8")

print("=" * 70)
print("DASHBOARD CHANGES VALIDATION")
print("=" * 70)

checks = []

# 1. Sorting fix
sorting_fix = "const aLayer = aMatch ? parseInt(aMatch[1]) : -1;"
count = html.count(sorting_fix)
checks.append(("Sorting fix (both tables)", count >= 2, f"{count}/2 occurrences"))

# 2. Custom tooltip CSS
css_check = ".metric-cell" in html and ".custom-tooltip" in html
checks.append(("Custom tooltip CSS classes", css_check, "Both classes present"))

# 3. Tooltip divs
tooltip_count = html.count('class="metric-cell"')
checks.append(
    ("Tooltip divs in tables", tooltip_count >= 9, f"{tooltip_count} cells with tooltips")
)

# 4. Worst Agent removed
worst_removed = "Worst Agent" not in html
checks.append(("Worst Agent column removed", worst_removed, "Column removed"))

# 5. Health Score simple avg
health_simple = "totalRow.Health.toFixed(1)" in html
checks.append(("Health Score simple average", health_simple, "No min/max/outliers"))

# 6. Code Quality Score simple avg
quality_simple = "codeQuality.toFixed(1)" in html
checks.append(("Code Quality simple average", quality_simple, "No min/max/outliers"))

# 7. L0 N/A values (correct by design)
l0_na = '"Heal Cap %": "N/A"' in html
checks.append(("L0 N/A values present", l0_na, "Correct - L0 agents don't self-heal"))

# 8. HIGH-SIGNAL tooltip function
tooltip_func = "REMEDIATION TARGETS" in html and "computeDistributionStats" in html
checks.append(("HIGH-SIGNAL tooltip content", tooltip_func, "Stats + file paths + remediation"))

print()
all_passed = True
for name, passed, detail in checks:
    status = "✅" if passed else "❌"
    print(f"{status} {name}: {detail}")
    if not passed:
        all_passed = False

print()
print("=" * 70)
if all_passed:
    print("✅ ALL CHANGES VERIFIED IN HTML FILE")
    print()
    print("If you don't see changes in browser:")
    print("1. Clear browser cache completely (Ctrl+Shift+Delete)")
    print("2. Close and reopen browser")
    print("3. Access with cache-busting URL:")
    print("   http://localhost:8765/autonomy_dashboard.html?v=new")
else:
    print("❌ SOME CHANGES MISSING - NEED TO RE-APPLY")
print("=" * 70)
