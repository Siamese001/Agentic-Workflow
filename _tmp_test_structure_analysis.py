"""Analyze test structure for ADG vs non-ADG tests."""
import sqlite3
import json
from pathlib import Path

db_path = r'C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_03152026_0344.sqlite'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 80)
print("TEST STRUCTURE ANALYSIS: ADG vs NON-ADG")
print("=" * 80)

# Find all test modules
cursor.execute("""
    SELECT adg_name, layer
    FROM nodes
    WHERE entity_type = 'repo_module' AND adg_name LIKE '%test%'
    ORDER BY layer, adg_name
""")
test_modules = cursor.fetchall()

print(f"\nTotal test modules: {len(test_modules)}")

# Group by layer
by_layer = {}
for mod, layer in test_modules:
    if layer not in by_layer:
        by_layer[layer] = []
    by_layer[layer].append(mod)

print("\nTest modules by layer:")
for layer in sorted(by_layer.keys()):
    print(f"  {layer}: {len(by_layer[layer])} modules")

# Find ADG-specific tests
cursor.execute("""
    SELECT adg_name
    FROM nodes
    WHERE entity_type = 'repo_module' 
    AND adg_name LIKE '%test%adg%'
    ORDER BY adg_name
""")
adg_tests = [row[0] for row in cursor.fetchall()]

print(f"\n\nADG-specific test modules: {len(adg_tests)}")
for test in adg_tests[:30]:
    print(f"  {test}")
if len(adg_tests) > 30:
    print(f"  ... and {len(adg_tests) - 30} more")

# Find guardian tests
cursor.execute("""
    SELECT adg_name
    FROM nodes
    WHERE entity_type = 'repo_module' 
    AND adg_name LIKE '%guardian%'
    ORDER BY adg_name
""")
guardian_tests = [row[0] for row in cursor.fetchall()]

print(f"\n\nGuardian-related modules: {len(guardian_tests)}")
for test in guardian_tests[:20]:
    print(f"  {test}")

# Find tests that cover ADG modules
cursor.execute("""
    SELECT DISTINCT n1.adg_name as test_module, n2.adg_name as covered_module
    FROM edges e
    JOIN nodes n1 ON e.src_id = n1.id
    JOIN nodes n2 ON e.dst_id = n2.id
    WHERE e.relation_type = 'covers'
    AND n1.adg_name LIKE '%test%'
    AND n2.adg_name LIKE '%adg%'
    ORDER BY n1.adg_name
    LIMIT 50
""")
adg_coverage = cursor.fetchall()

print(f"\n\nTests covering ADG modules (first 50):")
for test, covered in adg_coverage:
    print(f"  {test} -> {covered}")

conn.close()
print("\n" + "=" * 80)
