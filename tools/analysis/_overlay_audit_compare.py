"""Detail per-rename-shim comparison to validate the 50% recall."""

import json
from pathlib import Path

audit = json.loads(Path("docs/reports/plans/tech_debt_audit.json").read_text(encoding="utf-8"))
print("Audit-flagged shims (n=8):")
for r in audit["p1_rename_shims"]:
    f = r["file"]
    lines = r.get("lines", "?")
    classes = r.get("classes", [])
    marker = r.get("marker_excerpt", "")
    print(f"  lines={lines:>4}  classes={len(classes)} {f}")
    print(f"     marker: {marker[:80]}")
