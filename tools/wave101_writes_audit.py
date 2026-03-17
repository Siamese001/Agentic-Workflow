"""Wave 101: Audit writes_to vs writes_through alignment.

Find modules with writes_through but no writes_to, and vice versa.
Identify missing write-boundary patterns in the scanner.
"""
import glob
import os
import sqlite3
from collections import Counter

ADG_DIR = r"C:\Git\Agentic-Workflow\artifacts\adg"
pattern = os.path.join(ADG_DIR, "adg_indexed_*.sqlite")
files = sorted(glob.glob(pattern))
db_path = files[-1]
print(f"Using: {db_path}")

conn = sqlite3.connect(db_path)

# 1. Module-level alignment: writes_through vs writes_to
print("\n=== MODULE-LEVEL ALIGNMENT ===")

# Get source files with writes_through
wt_modules = set(r[0] for r in conn.execute(
    "SELECT DISTINCT source_file FROM edges WHERE relation_type='writes_through'"
).fetchall())

# Get source files with writes_to
wto_modules = set(r[0] for r in conn.execute(
    "SELECT DISTINCT source_file FROM edges WHERE relation_type='writes_to'"
).fetchall())

both = wt_modules & wto_modules
wt_only = wt_modules - wto_modules  # writes_through but no writes_to
wto_only = wto_modules - wt_modules  # writes_to but no writes_through

print(f"  Modules with writes_through:  {len(wt_modules)}")
print(f"  Modules with writes_to:       {len(wto_modules)}")
print(f"  Both:                          {len(both)}")
print(f"  writes_through only (gap):     {len(wt_only)}")
print(f"  writes_to only (uncovered):    {len(wto_only)}")

# 2. Edge-level: writes_to symbol distribution
print("\n=== WRITES_TO SYMBOL DISTRIBUTION (top 30) ===")
rows = conn.execute(
    "SELECT symbol, COUNT(*) as cnt FROM edges WHERE relation_type='writes_to' GROUP BY symbol ORDER BY cnt DESC LIMIT 30"
).fetchall()
for sym, cnt in rows:
    print(f"  {sym}: {cnt}")

# 3. Sample of writes_through-only modules (no writes_to)
print(f"\n=== SAMPLE: MODULES WITH writes_through BUT NO writes_to ({len(wt_only)} total) ===")
# Categorize by path prefix
prefix_counter = Counter()
for m in wt_only:
    parts = m.replace("\\", "/").split("/")
    prefix = parts[0] if parts else "unknown"
    prefix_counter[prefix] += 1

print("  By top-level directory:")
for prefix, cnt in prefix_counter.most_common(20):
    print(f"    {prefix}: {cnt}")

print("\n  First 30 modules (sorted):")
for m in sorted(wt_only)[:30]:
    print(f"    {m}")

# 4. Check what _GovernancePlaneVisitor matches for writes_through
print("\n=== WRITES_THROUGH EDGE SYMBOLS (what triggers governance write edges) ===")
rows = conn.execute(
    "SELECT symbol, COUNT(*) as cnt FROM edges WHERE relation_type='writes_through' GROUP BY symbol ORDER BY cnt DESC LIMIT 30"
).fetchall()
for sym, cnt in rows:
    print(f"  {sym}: {cnt}")

# 5. Check edge_kind distribution for writes_through
print("\n=== WRITES_THROUGH EDGE_KIND DISTRIBUTION ===")
rows = conn.execute(
    "SELECT edge_kind, COUNT(*) as cnt FROM edges WHERE relation_type='writes_through' GROUP BY edge_kind ORDER BY cnt DESC"
).fetchall()
for ek, cnt in rows:
    print(f"  {ek}: {cnt}")

# 6. Check what real write patterns exist in writes_through-only modules
# by looking at all edges from those modules
if wt_only:
    sample = sorted(wt_only)[:5]
    print("\n=== DETAILED EDGE AUDIT FOR 5 writes_through-only modules ===")
    for m in sample:
        print(f"\n  --- {m} ---")
        edges = conn.execute(
            "SELECT relation_type, symbol, edge_kind FROM edges WHERE source_file=? ORDER BY relation_type",
            (m,)
        ).fetchall()
        for rt, sym, ek in edges:
            if rt in ("writes_through", "writes_to", "calls"):
                print(f"    {rt}: {sym} [{ek}]")

conn.close()
