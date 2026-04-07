import collections
import sqlite3

db_path = r'C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_03132026_1902.sqlite'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 1. Total L_UNKNOWN count
cur.execute("SELECT COUNT(*) FROM nodes WHERE layer='L_UNKNOWN'")
total = cur.fetchone()[0]
print(f"Total L_UNKNOWN nodes: {total}")

# 2. Breakdown by entity_type
cur.execute("SELECT entity_type, COUNT(*) as cnt FROM nodes WHERE layer='L_UNKNOWN' GROUP BY entity_type ORDER BY cnt DESC")
print("\n--- By entity_type ---")
for row in cur.fetchall():
    print(f"  {row['entity_type']}: {row['cnt']}")

# 3. Breakdown by identity_kind
cur.execute("SELECT identity_kind, COUNT(*) as cnt FROM nodes WHERE layer='L_UNKNOWN' GROUP BY identity_kind ORDER BY cnt DESC")
print("\n--- By identity_kind ---")
for row in cur.fetchall():
    print(f"  {row['identity_kind']}: {row['cnt']}")

# 4. Breakdown by confidence
cur.execute("SELECT confidence, COUNT(*) as cnt FROM nodes WHERE layer='L_UNKNOWN' GROUP BY confidence ORDER BY cnt DESC")
print("\n--- By confidence ---")
for row in cur.fetchall():
    print(f"  {row['confidence']}: {row['cnt']}")

# 5. Top resolved_path prefixes (first 2 path segments) — all L_UNKNOWN
cur.execute("SELECT resolved_path FROM nodes WHERE layer='L_UNKNOWN' AND resolved_path IS NOT NULL AND resolved_path != ''")
paths = [row[0] for row in cur.fetchall()]
prefix_counts = collections.Counter()
for p in paths:
    parts = p.replace('\\', '/').split('/')
    prefix = '/'.join(parts[:2]) if len(parts) >= 2 else parts[0]
    prefix_counts[prefix] += 1
print("\n--- Top path prefixes (first 2 segments, all L_UNKNOWN with resolved_path) ---")
for prefix, cnt in prefix_counts.most_common(30):
    print(f"  {prefix}: {cnt}")

# 6. NULL or empty resolved_path count
cur.execute("SELECT COUNT(*) FROM nodes WHERE layer='L_UNKNOWN' AND (resolved_path IS NULL OR resolved_path = '')")
null_paths = cur.fetchone()[0]
print(f"\nL_UNKNOWN with null/empty resolved_path: {null_paths}")

# 7. NULL-path breakdown by identity_kind
cur.execute("""
    SELECT identity_kind, COUNT(*) as cnt
    FROM nodes
    WHERE layer='L_UNKNOWN' AND (resolved_path IS NULL OR resolved_path = '')
    GROUP BY identity_kind ORDER BY cnt DESC
""")
print("\n--- NULL-path L_UNKNOWN by identity_kind ---")
for row in cur.fetchall():
    print(f"  {row['identity_kind']}: {row['cnt']}")

# 8. repo_module nodes with L_UNKNOWN — full list grouped by top-level dir
cur.execute("""
    SELECT resolved_path
    FROM nodes
    WHERE layer='L_UNKNOWN' AND identity_kind='repo_module'
    ORDER BY resolved_path
""")
rm_paths = [row[0] for row in cur.fetchall()]
rm_prefix_counts = collections.Counter()
for p in rm_paths:
    parts = p.replace('\\', '/').split('/')
    prefix = parts[0] if parts else '(empty)'
    rm_prefix_counts[prefix] += 1
print(f"\n--- L_UNKNOWN repo_module nodes: {len(rm_paths)} total ---")
print("  Grouped by top-level directory:")
for prefix, cnt in rm_prefix_counts.most_common():
    print(f"    {prefix}: {cnt}")

# 9. inferred_symbol nodes with L_UNKNOWN — path prefix breakdown
cur.execute("""
    SELECT resolved_path
    FROM nodes
    WHERE layer='L_UNKNOWN' AND identity_kind='inferred_symbol'
    AND resolved_path IS NOT NULL AND resolved_path != ''
    ORDER BY resolved_path
""")
is_paths = [row[0] for row in cur.fetchall()]
is_prefix_counts = collections.Counter()
for p in is_paths:
    parts = p.replace('\\', '/').split('/')
    prefix = parts[0] if parts else '(empty)'
    is_prefix_counts[prefix] += 1
print(f"\n--- L_UNKNOWN inferred_symbol nodes with resolved_path: {len(is_paths)} total ---")
print("  Grouped by top-level directory:")
for prefix, cnt in is_prefix_counts.most_common():
    print(f"    {prefix}: {cnt}")

# 10. external_module symbols with L_UNKNOWN — how many, sample names
cur.execute("""
    SELECT COUNT(*) FROM nodes
    WHERE layer='L_UNKNOWN' AND identity_kind='external_module'
""")
ext_count = cur.fetchone()[0]
print(f"\n--- L_UNKNOWN external_module nodes: {ext_count} ---")

# 11. Cross-check: what layer does the layer_mapper assign to apps_eval/ and agentic_core/patterns/ ?
cur.execute("""
    SELECT layer, COUNT(*) as cnt FROM nodes
    WHERE (resolved_path LIKE 'apps_eval/%' OR resolved_path LIKE 'agentic_core/patterns/%')
    GROUP BY layer ORDER BY cnt DESC
""")
print("\n--- Layer distribution for apps_eval/ and agentic_core/patterns/ ---")
for row in cur.fetchall():
    print(f"  {row['layer']}: {row['cnt']}")

conn.close()
