# Found the bug! The validation logic requires ALL conditions to be true
print('=== ADG EDGE SEMANTIC PRECISION BUG FOUND ===')
print()

# The validation in generate_full_adg.py lines 1850-1858:
# passed = bool(
#     semantic_stats["semantic_edge_ratio"] >= 1.0           # ✅ 1.0 >= 1.0
#     and semantic_stats["execution_generic_semantic_count"] == 0  # ✅ 0 == 0
#     and semantic_stats["semantic_raw_edge_kind_count"] == 0     # ❌ 2 != 0
#     and semantic_stats["controls_flow_specific_ratio"] >= 0.95   # ✅ 1.0 >= 0.95
#     and semantic_stats["flows_to_specific_ratio"] >= 0.95       # ✅ 1.0 >= 0.95
#     and semantic_stats["side_effect_specific_ratio"] >= 0.95    # ✅ 1.0 >= 0.95
#     and semantic_stats["callsite_specific_ratio"] >= 0.95       # ✅ 1.0 >= 0.95
# )

print('ROOT CAUSE: semantic_raw_edge_kind_count == 0 condition is failing')
print()

# From the validation report evidence:
# semantic_raw_edge_kind_count: 2

print('Evidence shows:')
print('  semantic_raw_edge_kind_count: 2')
print('  Expected: 0')
print('  Actual: 2')
print()

print('This means there are 2 edges where the semantic_type is just the edge_kind')
print('(i.e., they fell through to the fallback: st = e.edge_kind)')
print()

# Let's find these problematic edges
import sqlite3

conn = sqlite3.connect('artifacts/adg/adg_indexed_03272026_1955.sqlite')

# Find edges where semantic_type == edge_kind
cursor = conn.execute('''
    SELECT DISTINCT edge_kind, semantic_type, COUNT(*)
    FROM edges
    WHERE semantic_type == edge_kind
    GROUP BY edge_kind, semantic_type
    ORDER BY COUNT(*) DESC
''')

problem_edges = cursor.fetchall()
print('Edges where semantic_type == edge_kind (raw edge kind fallback):')
for edge_kind, semantic_type, count in problem_edges:
    print(f'  {edge_kind}: {count} edges')

# Get total count
cursor = conn.execute('SELECT COUNT(*) FROM edges WHERE semantic_type == edge_kind')
total_raw_count = cursor.fetchone()[0]
print(f'\nTotal raw edge kind fallbacks: {total_raw_count}')

conn.close()

print()
print('FIX NEEDED: The semantic enrichment is missing mappings for these edge kinds')
print('Need to add them to _SEMANTIC_TYPE_MAP or _SEMANTIC_FALLBACK in static_scanner.py')
