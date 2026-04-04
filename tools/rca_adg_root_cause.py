# Root cause analysis of ADG semantic precision validation failure
import sqlite3

conn = sqlite3.connect('artifacts/adg/adg_indexed_03272026_1955.sqlite')

print('=== ADG EDGE SEMANTIC PRECISION ROOT CAUSE ===')
print()

# The validation is checking for execution edges with generic semantic types
# Generic semantics include: "execution", "call", "read", "write", "controls_flow",
# "flows_to", "emits_side_effect", "resolves_callsite"

generic_semantics = {
    "execution",
    "call",
    "read",
    "write",
    "controls_flow",
    "flows_to",
    "emits_side_effect",
    "resolves_callsite",
}

print("Checking execution edges for generic semantic types:")
print(f"Generic semantic types: {generic_semantics}")
print()

# Check execution edges with these generic semantic types
for semantic in generic_semantics:
    cursor = conn.execute('SELECT COUNT(*) FROM edges WHERE edge_kind = "execution" AND semantic_type = ?', (semantic,))
    count = cursor.fetchone()[0]
    if count > 0:
        print(f'  {semantic}: {count}')

# Total count
placeholders = ','.join(['?' for _ in generic_semantics])
cursor = conn.execute(f'SELECT COUNT(*) FROM edges WHERE edge_kind = "execution" AND semantic_type IN ({placeholders})', list(generic_semantics))
total_generic = cursor.fetchone()[0]

cursor = conn.execute('SELECT COUNT(*) FROM edges WHERE edge_kind = "execution"')
total_execution = cursor.fetchone()[0]

print(f'\nTotal execution edges with generic semantics: {total_generic}')
print(f'Total execution edges: {total_execution}')

# Calculate the ratio
ratio = total_generic / total_execution if total_execution > 0 else 0
print(f'Ratio: {ratio:.6f}')
print('Threshold: < 0.01 (1%)')

if ratio >= 0.01:
    print('\n❌ ROOT CAUSE FOUND: Too many execution edges have generic semantic types')
    print('This violates the semantic precision requirement')
else:
    print('\n✅ No issue found: Generic semantic ratio is acceptable')

# Let's check what semantic types execution edges actually have
print('\n=== ACTUAL EXECUTION EDGE SEMANTIC TYPES ===')
cursor = conn.execute('''
    SELECT semantic_type, COUNT(*)
    FROM edges
    WHERE edge_kind = "execution"
    GROUP BY semantic_type
    ORDER BY COUNT(*) DESC
    LIMIT 15
''')
semantic_types = cursor.fetchall()

for stype, count in semantic_types:
    is_generic = stype in generic_semantics
    marker = " ⚠️ GENERIC" if is_generic else ""
    print(f'  {stype}: {count}{marker}')

conn.close()
