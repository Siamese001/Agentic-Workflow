import collections
import sqlite3

db_path = r"C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_03132026_1902.sqlite"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 1. Total L_UNKNOWN count
cur.execute("SELECT COUNT(*) FROM nodes WHERE layer='L_UNKNOWN'")
total = cur.fetchone()[0]
print(f"Total L_UNKNOWN nodes: {total}")

# 2. Breakdown by entity_type
cur.execute(
    "SELECT entity_type, COUNT(*) as cnt FROM nodes WHERE layer='L_UNKNOWN' GROUP BY entity_type ORDER BY cnt DESC"
)
print("\n--- By entity_type ---")
for row in cur.fetchall():
    print(f"  {row['entity_type']}: {row['cnt']}")

# 3. Breakdown by identity_kind
cur.execute(
    "SELECT identity_kind, COUNT(*) as cnt FROM nodes WHERE layer='L_UNKNOWN' GROUP BY identity_kind ORDER BY cnt DESC"
)
print("\n--- By identity_kind ---")
for row in cur.fetchall():
    print(f"  {row['identity_kind']}: {row['cnt']}")

# 4. Breakdown by confidence
cur.execute(
    "SELECT confidence, COUNT(*) as cnt FROM nodes WHERE layer='L_UNKNOWN' GROUP BY confidence ORDER BY cnt DESC"
)
print("\n--- By confidence ---")
for row in cur.fetchall():
    print(f"  {row['confidence']}: {row['cnt']}")

# 5. Top resolved_path prefixes (first 2 path segments)
cur.execute(
    "SELECT resolved_path FROM nodes WHERE layer='L_UNKNOWN' AND resolved_path IS NOT NULL AND resolved_path != ''"
)
paths = [row[0] for row in cur.fetchall()]
prefix_counts = collections.Counter()
for p in paths:
    parts = p.replace("\\", "/").split("/")
    prefix = "/".join(parts[:2]) if len(parts) >= 2 else parts[0]
    prefix_counts[prefix] += 1
print("\n--- Top path prefixes (first 2 segments) ---")
for prefix, cnt in prefix_counts.most_common(25):
    print(f"  {prefix}: {cnt}")

# 6. NULL or empty resolved_path count
cur.execute(
    "SELECT COUNT(*) FROM nodes WHERE layer='L_UNKNOWN' AND (resolved_path IS NULL OR resolved_path = '')"
)
null_paths = cur.fetchone()[0]
print(f"\nL_UNKNOWN with null/empty resolved_path: {null_paths}")

# 7. Sample of actual resolved_paths for non-null
cur.execute("""
    SELECT resolved_path, entity_type, identity_kind, adg_name
    FROM nodes
    WHERE layer='L_UNKNOWN' AND resolved_path IS NOT NULL AND resolved_path != ''
    LIMIT 40
""")
print("\n--- Sample resolved_paths ---")
for row in cur.fetchall():
    print(f"  [{row['entity_type']}|{row['identity_kind']}] {row['adg_name']} -> {row['resolved_path']}")

# 8. Sample of null resolved_paths (adg_name tells us what they are)
cur.execute("""
    SELECT adg_name, entity_type, identity_kind
    FROM nodes
    WHERE layer='L_UNKNOWN' AND (resolved_path IS NULL OR resolved_path = '')
    LIMIT 40
""")
print("\n--- Sample NULL-path L_UNKNOWN nodes (adg_name) ---")
for row in cur.fetchall():
    print(f"  [{row['entity_type']}|{row['identity_kind']}] {row['adg_name']}")

# 9. Are any L_UNKNOWN nodes repo_modules that SHOULD have a layer?
cur.execute("""
    SELECT adg_name, resolved_path, identity_kind
    FROM nodes
    WHERE layer='L_UNKNOWN' AND identity_kind='repo_module'
    ORDER BY resolved_path
    LIMIT 40
""")
print("\n--- L_UNKNOWN repo_module nodes (should have layer!) ---")
rows = cur.fetchall()
print(f"  Count: {len(rows)}")
for row in rows:
    print(f"  {row['adg_name']} -> {row['resolved_path']}")

conn.close()
