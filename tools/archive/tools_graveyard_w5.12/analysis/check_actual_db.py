# Check what's actually in the database after stamping
import sqlite3

conn = sqlite3.connect("artifacts/adg/adg_indexed_03272026_2022.sqlite")

print("=== Checking actual database content ===")

# Check layer_membership edges specifically
cursor = conn.execute("""
    SELECT edge_kind, relation_type, semantic_type, COUNT(*)
    FROM edges
    WHERE edge_kind = "layer_membership"
    GROUP BY edge_kind, relation_type, semantic_type
""")
results = cursor.fetchall()

print("layer_membership edges:")
for edge_kind, rel_type, sem_type, count in results:
    print(f"  {edge_kind} + {rel_type} -> {sem_type}: {count}")

# Check if there's a mapping issue
print("\n=== Checking _SEMANTIC_TYPE_MAP for layer_membership ===")

# The issue might be that (edge_kind, relation_type) is in the exact map
# but with a different semantic_type than expected

from agentic_core.adg.extraction.static_scanner import _SEMANTIC_TYPE_MAP

key = ("layer_membership", "belongs_to_layer")
if key in _SEMANTIC_TYPE_MAP:
    print(f"Found in exact map: {key} -> {_SEMANTIC_TYPE_MAP[key]}")
else:
    print(f"Not found in exact map: {key}")

# Check fallback
from agentic_core.adg.extraction.static_scanner import _SEMANTIC_FALLBACK

if "belongs_to_layer" in _SEMANTIC_FALLBACK:
    print(f"Found in fallback: belongs_to_layer -> {_SEMANTIC_FALLBACK['belongs_to_layer']}")
else:
    print("Not found in fallback: belongs_to_layer")

conn.close()
