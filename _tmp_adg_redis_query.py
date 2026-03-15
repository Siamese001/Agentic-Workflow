"""Query ADG SQLite to analyze Redis cache layer architecture."""
import sqlite3
import json

db_path = r'C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_03152026_0344.sqlite'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 80)
print("ADG DATABASE SCHEMA")
print("=" * 80)
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print(f"\nTables: {', '.join(tables)}\n")

for table in tables:
    cursor.execute(f"PRAGMA table_info({table})")
    cols = cursor.fetchall()
    print(f"\n{table}:")
    for col in cols:
        print(f"  - {col[1]} ({col[2]})")

print("\n" + "=" * 80)
print("REDIS CACHE LAYER ANALYSIS")
print("=" * 80)

# Find all Redis-related nodes
cursor.execute("""
    SELECT adg_name, entity_type, layer, confidence 
    FROM nodes 
    WHERE adg_name LIKE '%redis%' OR adg_name LIKE '%cache%'
    ORDER BY layer, adg_name
    LIMIT 50
""")
print("\n1. Redis/Cache Nodes (first 50):")
for row in cursor.fetchall():
    print(f"  {row[0]} | {row[1]} | {row[2]} | {row[3]}")

# Find retrieves_via edges (RAG retrieval pattern)
cursor.execute("""
    SELECT n1.adg_name, n2.adg_name, e.relation_type
    FROM edges e
    JOIN nodes n1 ON e.src_id = n1.id
    JOIN nodes n2 ON e.dst_id = n2.id
    WHERE e.relation_type = 'retrieves_via'
    LIMIT 30
""")
print("\n2. retrieves_via edges (RAG retrieval pattern):")
for row in cursor.fetchall():
    print(f"  {row[0]} -> {row[1]} ({row[2]})")

# Find semantic cache related edges
cursor.execute("""
    SELECT DISTINCT n1.adg_name, n2.adg_name, e.relation_type
    FROM edges e
    JOIN nodes n1 ON e.src_id = n1.id
    JOIN nodes n2 ON e.dst_id = n2.id
    WHERE n1.adg_name LIKE '%semantic_cache%' OR n2.adg_name LIKE '%semantic_cache%'
    ORDER BY e.relation_type, n1.adg_name
    LIMIT 40
""")
print("\n3. Semantic Cache Edges (first 40):")
for row in cursor.fetchall():
    print(f"  {row[0]} -> {row[1]} ({row[2]})")

# Find Redis cache client usage
cursor.execute("""
    SELECT DISTINCT n1.adg_name, n2.adg_name, e.relation_type
    FROM edges e
    JOIN nodes n1 ON e.src_id = n1.id
    JOIN nodes n2 ON e.dst_id = n2.id
    WHERE n1.adg_name LIKE '%redis_cache_client%' OR n2.adg_name LIKE '%redis_cache_client%'
    ORDER BY e.relation_type, n1.adg_name
    LIMIT 40
""")
print("\n4. Redis Cache Client Edges (first 40):")
for row in cursor.fetchall():
    print(f"  {row[0]} -> {row[1]} ({row[2]})")

# Find vector DB / embedding related edges
cursor.execute("""
    SELECT DISTINCT n1.adg_name, n2.adg_name, e.relation_type
    FROM edges e
    JOIN nodes n1 ON e.src_id = n1.id
    JOIN nodes n2 ON e.dst_id = n2.id
    WHERE e.relation_type IN ('embeds_into', 'stores_embedding', 'retrieves_via')
    ORDER BY e.relation_type, n1.adg_name
    LIMIT 40
""")
print("\n5. Vector DB / Embedding Edges (first 40):")
for row in cursor.fetchall():
    print(f"  {row[0]} -> {row[1]} ({row[2]})")

# Find cache mixin usage
cursor.execute("""
    SELECT DISTINCT n1.adg_name, n2.adg_name, e.relation_type
    FROM edges e
    JOIN nodes n1 ON e.src_id = n1.id
    JOIN nodes n2 ON e.dst_id = n2.id
    WHERE n2.adg_name LIKE '%cache_mixin%'
    ORDER BY n1.adg_name
    LIMIT 40
""")
print("\n6. Cache Mixin Usage (first 40):")
for row in cursor.fetchall():
    print(f"  {row[0]} -> {row[1]} ({row[2]})")

conn.close()
print("\n" + "=" * 80)
