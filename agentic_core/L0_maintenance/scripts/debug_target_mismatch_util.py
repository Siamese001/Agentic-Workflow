"""Debug which territories have mismatched targets."""

import json
import re
from pathlib import Path

dashboard_path = Path("reports/autonomy_dashboard.html")
html = dashboard_path.read_text(encoding="utf-8")

data_match = re.search(r"const dashboardData = (\[.*?\]);", html, re.DOTALL)
rows = json.loads(data_match.group(1))

non_total = [r for r in rows if r.get("Territory") != "TOTAL"]

print("Checking all territories for target mismatches:\n")

mismatches = []
for row in non_total:
    target_inv = row.get("Target Invocation")
    territory = row.get("Territory", "")

    expected = None
    if "L0 Maintenance" in territory:
        if "Infrastructure" in territory or "Infrast" in territory:
            expected = 70
        else:
            expected = 20
    elif "Infrastructure" in territory or "Infrast" in territory:
        expected = 70
    elif "Base Cl" in territory:
        expected = "N/A"
    else:
        expected = 100

    if target_inv != expected:
        mismatches.append((territory, target_inv, expected))
        print(f"❌ {territory}")
        print(f"   Actual: {target_inv}, Expected: {expected}\n")

if not mismatches:
    print("✅ All territories have correct targets!")
else:
    print(f"\nTotal mismatches: {len(mismatches)}")
