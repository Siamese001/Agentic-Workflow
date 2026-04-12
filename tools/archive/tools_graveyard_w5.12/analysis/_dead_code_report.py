"""
ADG Dead Code Report — uses pre-tagged dead_imports + unused_import edges,
plus corrected zero-fan-in module analysis (src=importer, dst=importee).
"""

import sqlite3
from collections import defaultdict

DB = r"C:\\Git\\Agentic-Workflow\\artifacts\\adg\\adg_indexed_04072026_1002.sqlite"
conn = sqlite3.connect(DB)
c = conn.cursor()

PROD_PREFIXES = ("agentic_core/", "apps_", "system_learning/", "infrastructure/")


def is_prod(path):
    if not path:
        return False
    return any(path.startswith(p) for p in PROD_PREFIXES)


# ── 1. ADG-tagged dead_imports edges (modules nobody uses) ──────────────────
print("=" * 70)
print("SECTION 1: ADG-tagged dead_imports edges")
print("=" * 70)
dead_import_rows = c.execute("""
    SELECT e.source_file, e.symbol, n_dst.resolved_path
    FROM edges e
    LEFT JOIN nodes n_dst ON e.dst_id = n_dst.id
    WHERE e.relation_type = 'dead_imports'
    ORDER BY e.source_file, e.symbol
""").fetchall()

by_file = defaultdict(list)
for src_file, symbol, dst_path in dead_import_rows:
    if is_prod(src_file):
        by_file[src_file].append((symbol, dst_path))

print(f"Total dead_imports edges in production files: {sum(len(v) for v in by_file.values())}")
for f in sorted(by_file):
    print(f"\n  FILE: {f}")
    for sym, dst in by_file[f]:
        print(f"    dead import: {sym}  (from {dst})")

# ── 2. unused_import edges in production files ───────────────────────────────
print("\n" + "=" * 70)
print("SECTION 2: unused_import edges in production files")
print("=" * 70)
unused_rows = c.execute("""
    SELECT e.source_file, e.symbol, n_dst.resolved_path
    FROM edges e
    LEFT JOIN nodes n_dst ON e.dst_id = n_dst.id
    WHERE e.relation_type = 'unused_import'
    ORDER BY e.source_file, e.symbol
""").fetchall()

by_file2 = defaultdict(list)
for src_file, symbol, dst_path in unused_rows:
    if is_prod(src_file):
        by_file2[src_file].append((symbol, dst_path))

print(f"Total unused_import edges in production files: {sum(len(v) for v in by_file2.values())}")
for f in sorted(by_file2):
    print(f"\n  FILE: {f}")
    for sym, dst in by_file2[f]:
        print(f"    unused: {sym}  (from {dst})")

# ── 3. Zero-fan-in production MODULES (fixed: fan-in = appears as dst in imports) ──
print("\n" + "=" * 70)
print("SECTION 3: Zero-fan-in production modules")
print("(no other production module imports them)")
print("=" * 70)

# All production module node IDs
prod_mod_query = """
SELECT id, adg_name, resolved_path, layer
FROM nodes
WHERE entity_type = 'module'
  AND resolved_path NOT LIKE '%/__pycache__/%'
  AND resolved_path NOT LIKE '%__init__.py'
"""
all_mods = {r[0]: (r[1], r[2], r[3]) for r in c.execute(prod_mod_query).fetchall()}
prod_mods = {nid: info for nid, info in all_mods.items() if is_prod(info[1])}

# Node IDs that appear as dst in 'imports' edges (i.e. are imported by someone)
# dst can be symbol nodes — resolve to their resolved_path file
imported_paths = set(
    r[0]
    for r in c.execute("""
        SELECT DISTINCT n.resolved_path
        FROM edges e
        JOIN nodes n ON e.dst_id = n.id
        WHERE e.relation_type = 'imports'
    """).fetchall()
    if r[0]
)

dead_mods = [
    (info[1], info[2]) for nid, info in prod_mods.items() if info[1] not in imported_paths
]  # resolved_path not in imported set
dead_mods.sort(key=lambda x: (x[1], x[0]))  # sort by layer then path

by_layer3 = defaultdict(list)
for path, layer in dead_mods:
    by_layer3[layer].append(path)

print(f"Zero-fan-in production modules: {len(dead_mods)}")
for layer in sorted(by_layer3):
    paths = sorted(by_layer3[layer])
    print(f"\n  === {layer} ({len(paths)}) ===")
    for p in paths:
        print(f"    {p}")

conn.close()
