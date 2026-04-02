import sqlite3

conn = sqlite3.connect('artifacts/adg/adg_indexed_03242026_1825.sqlite')
cursor = conn.cursor()

# Get all layer gravity violations
cursor.execute('''
SELECT n1.adg_name as src_module, n2.adg_name as target_layer, e.source_file, e.line_no, e.symbol
FROM edges e
JOIN nodes n1 ON e.src_id = n1.id
JOIN nodes n2 ON e.dst_id = n2.id
WHERE e.relation_type = "violates" AND e.edge_kind = "import"
ORDER BY e.source_file, e.line_no
''')
violations = cursor.fetchall()

print(f'Layer Gravity Violations: {len(violations)}')
print('=' * 80)

# Group by source layer to see the pattern
from collections import defaultdict
src_layers = defaultdict(list)
for src, target, file, line, symbol in violations:
    src_layer = src.split('::')[1].split('/')[0]  # Extract L0, L1, etc.
    src_layers[src_layer].append((src, target, file, line, symbol))

print('Violations by source layer:')
for src_layer, vlist in sorted(src_layers.items()):
    print(f'\n{src_layer} -> L_RUNTIME violations ({len(vlist)}):')
    for src, target, file, line, symbol in vlist[:3]:  # Show first 3
        print(f'  {src} importing {symbol} from {target}')
    if len(vlist) > 3:
        print(f'  ... and {len(vlist) - 3} more')

# Check what's being imported from L_RUNTIME
print('\n' + '=' * 80)
print('What L_RUNTIME contains:')
cursor.execute('SELECT adg_name FROM nodes WHERE adg_name LIKE "ADG::Layer::L_RUNTIME"')
runtime_layer = cursor.fetchone()
if runtime_layer:
    cursor.execute('''
    SELECT n.adg_name, e.symbol
    FROM edges e
    JOIN nodes n ON e.dst_id = n.id
    WHERE e.src_id = (SELECT id FROM nodes WHERE adg_name = ?) AND e.relation_type = "belongs_to_layer"
    ''', (runtime_layer[0],))
    runtime_modules = cursor.fetchall()
    print(f'L_RUNTIME has {len(runtime_modules)} modules:')
    for module, symbol in runtime_modules[:5]:
        print(f'  {module} ({symbol})')
    if len(runtime_modules) > 5:
        print(f'  ... and {len(runtime_modules) - 5} more')

conn.close()
