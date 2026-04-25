import sqlite3, glob, os

db = sorted(glob.glob("artifacts/adg/adg_debt_overlay_*.sqlite"), key=os.path.getmtime)[-1]
print("overlay:", os.path.basename(db))
con = sqlite3.connect(db)
con.row_factory = sqlite3.Row

print("\n=== sample dead_import (10) ===")
for r in con.execute(
    "SELECT module, source_file, line_no, name FROM overlay_imports WHERE status='missing' LIMIT 10"
):
    print(f"  L{r['line_no']:4d} {r['source_file']}")
    print(f"         from {r['module']} import {r['name']}")

print("\n=== top dead-import targets (modules) ===")
for r in con.execute(
    "SELECT module, COUNT(*) c FROM overlay_imports WHERE status='missing' GROUP BY module ORDER BY c DESC LIMIT 15"
):
    print(f"  {r['c']:5d}  {r['module']}")

print("\n=== top namespace_pkg_import targets ===")
for r in con.execute(
    "SELECT module, COUNT(*) c FROM overlay_imports WHERE status='namespace_pkg' GROUP BY module ORDER BY c DESC LIMIT 15"
):
    print(f"  {r['c']:5d}  {r['module']}")

print("\n=== module_duplicate clusters (top 15 by size) ===")
for r in con.execute("SELECT cluster_size, hash, files FROM mv_duplicate_module_clusters LIMIT 15"):
    print(f"  cluster={r['cluster_size']:3d}  hash={r['hash'][:12]}")
    for f in r["files"].split("|")[:3]:
        print(f"       {f}")
    if r["cluster_size"] > 3:
        print(f"       ... +{r['cluster_size'] - 3} more")

print("\n=== rename shim hits ===")
for r in con.execute(
    "SELECT file_path, evidence FROM overlay_violations WHERE category='rename_shim_module'"
):
    print(f"  {r['file_path']}  marker={r['evidence']}")

print("\n=== fallback_stub samples ===")
for r in con.execute(
    "SELECT file_path, line_no, evidence, detail FROM overlay_violations WHERE category='import_error_fallback_stub' LIMIT 15"
):
    print(f"  {r['file_path']}:L{r['line_no']}  class={r['evidence']}  ({r['detail']})")

print("\n=== stale_all sample ===")
for r in con.execute(
    "SELECT file_path, evidence FROM overlay_violations WHERE category='stale_all_export' LIMIT 15"
):
    print(f"  {r['file_path']}  missing={r['evidence']}")

print("\n=== top module_load_action_call files ===")
for r in con.execute(
    "SELECT file_path, evidence FROM overlay_violations WHERE category='module_load_action_call' ORDER BY CAST(SUBSTR(evidence,9) AS INTEGER) DESC LIMIT 15"
):
    print(f"  {r['evidence']}  {r['file_path']}")
