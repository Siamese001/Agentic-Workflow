"""Verify the enriched canonical SQLite has all overlay data."""

# W6 ADG consumer mode declaration (per .windsurf/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import sqlite3

con = sqlite3.connect("artifacts/adg/adg_indexed_04242026_0558_test.sqlite")
con.row_factory = sqlite3.Row
cur = con.cursor()

print("=== schema check ===")
n_body_hash = cur.execute("SELECT COUNT(*) FROM nodes WHERE body_hash IS NOT NULL").fetchone()[0]
print(f"  nodes.body_hash populated:  {n_body_hash}")

print("\n=== overlay_violations summary ===")
for r in cur.execute("SELECT * FROM mv_overlay_debt_summary"):
    print(f"  {r['severity']:9s}  {r['n_rows']:6d}  {r['category']}")

print("\n=== top dead-import targets (from canonical-snapshot overlay) ===")
for r in cur.execute(
    "SELECT evidence, COUNT(*) c FROM overlay_violations "
    "WHERE category='dead_import_resolved' "
    "GROUP BY substr(evidence, 1, instr(evidence, ' ')-1) "
    "ORDER BY c DESC LIMIT 10"
):
    print(f"  {r['c']:5d}  {r['evidence'][:80]}")

print("\n=== top dead-import hotspot files ===")
for r in cur.execute("SELECT * FROM mv_dead_import_hotspots_overlay LIMIT 10"):
    print(f"  {r['dead_count']:4d}  {r['file']}")

print("\n=== module duplicate clusters (top 10) ===")
for r in cur.execute("SELECT * FROM mv_module_duplicate_clusters_overlay LIMIT 10"):
    print(f"  cluster={r['cluster_size']:3d}  hash={r['body_hash'][:12]}")
    for f in (r["files"] or "").split("|")[:3]:
        print(f"        {f}")
    if r["cluster_size"] > 3:
        print(f"        ... +{r['cluster_size'] - 3} more")

print("\n=== rename shim files ===")
for r in cur.execute(
    "SELECT file_path, evidence FROM overlay_violations WHERE category='rename_shim_module'"
):
    print(f"  {r['file_path']}  → {r['evidence']}")

print("\n=== schema sizes ===")
for tab in ("nodes", "edges", "violations", "overlay_violations"):
    n = cur.execute(f"SELECT COUNT(*) FROM {tab}").fetchone()[0]
    print(f"  {tab:25s}  {n}")

print("\n=== canonical violations untouched? ===")
n_canonical_classes = cur.execute(
    "SELECT violation_class, COUNT(*) FROM violations GROUP BY violation_class"
).fetchall()
for r in n_canonical_classes:
    print(f"  {r[0]:20s}  {r[1]}")
con.close()
