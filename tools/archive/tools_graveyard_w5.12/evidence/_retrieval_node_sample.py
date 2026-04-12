"""Sample nodes and edges to understand actual id/path formats."""

import sqlite3

SQLITE_PATH = r"C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_03312026_1808.sqlite"
conn = sqlite3.connect(SQLITE_PATH)
cur = conn.cursor()

print("=== SAMPLE NODES (10) ===")
cur.execute("SELECT id, adg_name, entity_type, layer, resolved_path FROM nodes LIMIT 10")
for r in cur.fetchall():
    print(r)

print("\n=== SAMPLE EDGES (5) ===")
cur.execute(
    "SELECT src_id, dst_id, relation_type, source_file FROM edges WHERE relation_type='reads_from' LIMIT 5"
)
for r in cur.fetchall():
    print(r)

print("\n=== NODES CONTAINING 'L1_cognition' in id ===")
cur.execute("SELECT id, resolved_path FROM nodes WHERE id LIKE '%L1_cognition%' LIMIT 5")
for r in cur.fetchall():
    print(r)

print("\n=== NODES CONTAINING 'L1_cognition' in resolved_path ===")
cur.execute("SELECT id, resolved_path FROM nodes WHERE resolved_path LIKE '%L1_cognition%' LIMIT 5")
for r in cur.fetchall():
    print(r)

print("\n=== EDGES with source_file containing 'L1_cognition' (5) ===")
cur.execute(
    "SELECT src_id, dst_id, relation_type, source_file FROM edges WHERE source_file LIKE '%L1_cognition%' LIMIT 5"
)
for r in cur.fetchall():
    print(r)

print("\n=== EDGES with source_file containing 'apps_lic' (5) ===")
cur.execute(
    "SELECT src_id, dst_id, relation_type, source_file FROM edges WHERE source_file LIKE '%apps_lic%' LIMIT 5"
)
for r in cur.fetchall():
    print(r)

print("\n=== NODES containing 'retrieval' in id ===")
cur.execute("SELECT id, resolved_path FROM nodes WHERE id LIKE '%retrieval%' LIMIT 10")
for r in cur.fetchall():
    print(r)

print("\n=== NODES containing 'chunk' in id ===")
cur.execute("SELECT id, resolved_path FROM nodes WHERE id LIKE '%chunk%' LIMIT 10")
for r in cur.fetchall():
    print(r)

print("\n=== NODES containing 'embed' in id ===")
cur.execute("SELECT id, resolved_path FROM nodes WHERE id LIKE '%embed%' LIMIT 10")
for r in cur.fetchall():
    print(r)

print("\n=== NODES containing 'rag' in id (case insensitive) ===")
cur.execute("SELECT id, resolved_path FROM nodes WHERE lower(id) LIKE '%rag%' LIMIT 10")
for r in cur.fetchall():
    print(r)

print("\n=== SRC->DST cross-layer check: edges where src_id has L1 and dst_id has L4 ===")
cur.execute("""
    SELECT COUNT(*) FROM edges e
    WHERE e.src_id LIKE '%L1_cognition%' AND e.dst_id LIKE '%L4_state%'
""")
print("L1->L4:", cur.fetchone()[0])

print("\n=== source_file cross-layer (L1 source -> node with L4 in id) ===")
cur.execute("""
    SELECT COUNT(*) FROM edges e
    JOIN nodes n_dst ON e.dst_id = n_dst.id
    WHERE e.source_file LIKE '%L1_cognition%'
      AND n_dst.id LIKE '%L4_state%'
""")
print("L1 source_file -> L4 node:", cur.fetchone()[0])

conn.close()
