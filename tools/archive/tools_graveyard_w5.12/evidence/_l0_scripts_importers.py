"""Use ADG edges to find what imports L0_routing/scripts/* modules."""

import pathlib
import sqlite3
from collections import defaultdict

DB = pathlib.Path("artifacts/adg/adg_indexed_03122026.sqlite")
conn = sqlite3.connect(DB)

# Who imports from L0_routing/scripts/?  Join nodes to get resolved_path of dst
print("=== Files that IMPORT from L0_routing/scripts/ ===")
rows = conn.execute(
    "SELECT e.source_file, n.resolved_path, e.symbol FROM edges e "
    "JOIN nodes n ON n.id = e.dst_id "
    "WHERE e.relation_type='imports' AND n.resolved_path LIKE '%L0_routing/scripts/%' "
    "ORDER BY n.resolved_path, e.source_file",
).fetchall()

by_target = defaultdict(list)
for src, tgt, sym in rows:
    by_target[tgt].append(src)

for tgt in sorted(by_target):
    importers = by_target[tgt]
    print(f"\n  {tgt}  ({len(importers)} importer(s))")
    for imp in importers:
        print(f"    <- {imp}")

print(f"\nTotal script files imported by other modules: {len(by_target)}")

# Scripts that are violators but have NO importers (safe to move)
print("\n=== L0_routing/scripts/ violators with ZERO importers (safe to move) ===")
violating = conn.execute(
    "SELECT DISTINCT e.source_file FROM edges e "
    "WHERE e.relation_type='violates' AND e.source_file LIKE '%L0_routing/scripts/%'",
).fetchall()
violating_set = {r[0] for r in violating}
imported_targets = set(by_target.keys())
standalone_violators = sorted(f for f in violating_set if f not in imported_targets)
print(f"Count: {len(standalone_violators)}")
for f in standalone_violators:
    print(f"  {f}")

conn.close()
