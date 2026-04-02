# Deep analysis of the ADG semantic precision issue
import sqlite3

conn = sqlite3.connect('artifacts/adg/adg_indexed_03272026_1955.sqlite')

# 1. Check the validation requirements
print('=== ADG EDGE SEMANTIC PRECISION RCA ===')
print()

# Check execution edges specifically
cursor = conn.execute('SELECT COUNT(*) FROM edges WHERE edge_kind = "execution"')
execution_total = cursor.fetchone()[0]
print(f'Total execution edges: {execution_total}')

# Check generic semantic types for execution edges
generic_semantics = ['execution', 'execution_generic', 'execution_trace']
cursor = conn.execute('SELECT COUNT(*) FROM edges WHERE edge_kind = "execution" AND semantic_type IN (?, ?, ?)', generic_semantics)
execution_generic = cursor.fetchone()[0]
print(f'Execution edges with generic semantic types: {execution_generic}')

# Check expected semantic types for execution
expected_execution_semantics = [
    'attribute_dispatch', 'branch', 'loop', 'invokes_function',
    'instantiates_class', 'dynamic_getattr', 'dynamic_exec', 'eval_call'
]
cursor = conn.execute('SELECT COUNT(*) FROM edges WHERE edge_kind = "execution" AND semantic_type IN ({})'.format(
    ','.join(['?' for _ in expected_execution_semantics])
), expected_execution_semantics)
execution_specific = cursor.fetchone()[0]
print(f'Execution edges with specific semantic types: {execution_specific}')

# Check what semantic types actually exist for execution edges
cursor = conn.execute('SELECT DISTINCT semantic_type, COUNT(*) FROM edges WHERE edge_kind = "execution" GROUP BY semantic_type ORDER BY COUNT(*) DESC LIMIT 10')
execution_semantic_types = cursor.fetchall()
print('\nTop 10 semantic types for execution edges:')
for stype, count in execution_semantic_types:
    print(f'  {stype}: {count}')

# Check validation threshold
print('\n=== VALIDATION ANALYSIS ===')
print(f'Generic semantic ratio: {execution_generic}/{execution_total} = {execution_generic/execution_total if execution_total > 0 else 0:.4f}')
print(f'Expected threshold: < 0.01 (1%)')
print(f'Actual ratio: {execution_generic/execution_total if execution_total > 0 else 0:.4f}')

# Check if this is the issue
generic_ratio = execution_generic / execution_total if execution_total > 0 else 0
if generic_ratio >= 0.01:
    print('❌ ISSUE CONFIRMED: Too many execution edges have generic semantic types')
else:
    print('✅ Execution edges semantic precision is acceptable')

conn.close()
