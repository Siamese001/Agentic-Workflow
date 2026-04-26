"""Check whether existing ADG CI gates already cover the 89 P0/HIGH/CRITICAL rows from AUDIT_6."""
import sqlite3
import glob
import json
from pathlib import Path

snap = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
print(f"Snapshot: {snap}")
c = sqlite3.connect(snap)

print("\n=== Severity distribution in violations table ===")
for sev, n in c.execute("SELECT severity, COUNT(*) FROM violations GROUP BY severity ORDER BY 2 DESC"):
    print(f"  {sev!s:<15} {n}")

print("\n=== Band distribution (if column exists) ===")
cols = [r[1] for r in c.execute("PRAGMA table_info(violations)")]
print(f"  violations columns: {cols}")

if "band" in cols:
    for band, n in c.execute("SELECT band, COUNT(*) FROM violations GROUP BY band ORDER BY 2 DESC"):
        print(f"  {band!s:<10} {n}")

print("\n=== Existing ratchet baselines mentioning P0/severity ===")
bdir = Path("ops_scripts/ci/baselines")
for bf in sorted(bdir.glob("*.json")):
    try:
        data = json.loads(bf.read_text())
    except (json.JSONDecodeError, OSError):
        continue
    txt = json.dumps(data).lower()
    if any(k in txt for k in ("p0", "critical", "high", "severity")):
        # Top-level info
        top_keys = list(data.keys())[:5] if isinstance(data, dict) else ["<list>"]
        count = data.get("count", data.get("current", data.get("ceiling", "?"))) if isinstance(data, dict) else "?"
        print(f"  {bf.name:<50} top_keys={top_keys}  count={count}")

print("\n=== The 89 AUDIT_6 rows: what severities? ===")
rows = list(c.execute(
    "SELECT severity, COUNT(*) FROM violations "
    "WHERE (triage_status IS NULL OR triage_status='' OR triage_status='untriaged') "
    "AND severity IN ('HIGH','CRITICAL','P0') "
    "GROUP BY severity"
))
for sev, n in rows:
    print(f"  {sev!s:<15} {n}")

print("\n=== Does P0 ratchet (check_overlay_ratchet.py) currently enforce count<=0? ===")
ovb = bdir / "overlay_ratchet.json"
if ovb.exists():
    print(f"  overlay_ratchet.json:\n  {ovb.read_text()[:500]}")
