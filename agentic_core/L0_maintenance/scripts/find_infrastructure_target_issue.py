"""Find which Infrastructure territory has wrong target."""

import json
import re
from pathlib import Path

dashboard_path = Path("reports/autonomy_dashboard.html")
html = dashboard_path.read_text(encoding="utf-8")

data_match = re.search(r"const dashboardData = (\[.*?\]);", html, re.DOTALL)
rows = json.loads(data_match.group(1))

non_total = [r for r in rows if r.get("Territory") != "TOTAL"]
infra_rows = [
    r
    for r in non_total
    if "Infrastructure" in r.get("Territory", "") or "Infrast" in r.get("Territory", "")
]

print(f"Found {len(infra_rows)} Infrastructure territories:\n")
for row in infra_rows:
    terr = row.get("Territory")
    target_inv = row.get("Target Invocation")
    print(f"  {terr}: Target = {target_inv}")
    if target_inv == 20:
        print("    ⚠️  WRONG! Should be 70")
