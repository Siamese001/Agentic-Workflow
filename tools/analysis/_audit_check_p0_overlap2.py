import glob
import logging
import sqlite3

snap = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
c = sqlite3.connect(snap)

cols = [r[1] for r in c.execute("PRAGMA table_info(violations)")]
print(f"violations columns: {cols}\n")
logging.info("C3 write receipt: tools/analysis/_audit_check_p0_overlap2.py write side effect recorded")

print("=== HIGH+CRITICAL rows by antipattern/category ===")
ap_col = "antipattern" if "antipattern" in cols else ("category" if "category" in cols else "violation_class")
print(f"(using column: {ap_col})")
q = f"SELECT {ap_col}, severity, COUNT(*) FROM violations WHERE severity IN ('HIGH','CRITICAL') GROUP BY {ap_col}, severity ORDER BY 3 DESC"
for row in c.execute(q):
    print(f"  {str(row[0]):<40} {row[1]:<10} {row[2]}")

print("\n=== P0/P1/P2/P3 views and row counts ===")
views = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='view' AND name LIKE 'v_p%'")]
for v in views[:20]:
    try:
        n = c.execute(f"SELECT COUNT(*) FROM {v}").fetchone()[0]
        print(f"  {v:<50} rows={n}")
    except sqlite3.OperationalError as e:
        print(f"  {v:<50} ERR: {str(e)[:40]}")

print("\n=== Cross: are HIGH/CRITICAL violations already in v_p0_* views? ===")
# Pick first v_p0 view, see if it intersects violations.severity
if any(v.startswith("v_p0_") for v in views):
    v0 = [v for v in views if v.startswith("v_p0_")][0]
    v0_cols = [r[1] for r in c.execute(f"PRAGMA table_info({v0})")]
    print(f"  {v0} columns: {v0_cols}")

print("\n=== Existing gates that consume violations.severity ===")
import subprocess

r = subprocess.run(["grep", "-rln", "severity.*HIGH\\|severity.*CRITICAL", "ops_scripts/ci/"], capture_output=True, text=True)
print(r.stdout or "  (none found via grep)")
