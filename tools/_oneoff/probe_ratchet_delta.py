"""
Find MEDIUM antipattern violations NOT in the last stored snapshot.
Runs the ADG scanner directly (same logic as generate_full_adg) but
only up to the violation-scan stage, then compares against the stored DB.
"""
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# ---- Load stored snapshot violations ----
snapshots = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"))
if not snapshots:
    print("No snapshot found")
    sys.exit(1)

stored = snapshots[-1]
print(f"Stored snapshot: {stored}")

con = sqlite3.connect(stored)
stored_rows = set()
for fp, ln, cat in con.execute(
    "SELECT file_path, line_no, category FROM violations WHERE severity='MEDIUM' AND category='antipattern'"
).fetchall():
    stored_rows.add((fp, ln))
con.close()
print(f"Stored MEDIUM antipattern count: {len(stored_rows)}")

# ---- Scan current codebase via ADG scanner ----
try:
    from tools.adg.core.scanner import scan_antipatterns
    fresh = scan_antipatterns(root=ROOT)
    fresh_medium = [(r["file_path"], r["line_no"], r.get("antipattern_type", "-")) for r in fresh if r.get("severity") == "MEDIUM"]
    print(f"Fresh scan MEDIUM count: {len(fresh_medium)}")
    new_violations = [(fp, ln, ap) for fp, ln, ap in fresh_medium if (str(fp), ln) not in stored_rows and (fp, ln) not in stored_rows]
    print(f"\nNew violations not in stored snapshot ({len(new_violations)}):")
    for fp, ln, ap in sorted(new_violations):
        print(f"  {fp}:{ln}  ap={ap}")
except ImportError as e:
    print(f"Scanner import failed: {e}")
    print("Cannot do live scan - check import path")
