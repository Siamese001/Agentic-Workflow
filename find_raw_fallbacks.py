# Find which edges are actually falling back to raw edge_kind
import sqlite3

conn = sqlite3.connect('artifacts/adg/adg_indexed_03272026_2022.sqlite')

print('=== Finding raw edge_kind fallbacks ===')

# Find edges where semantic_type == edge_kind (raw fallbacks)
cursor = conn.execute('''
    SELECT edge_kind, relation_type, COUNT(*) 
    FROM edges 
    WHERE semantic_type == edge_kind 
    GROUP BY edge_kind, relation_type 
    ORDER BY COUNT(*) DESC
    LIMIT 20
''')

results = cursor.fetchall()

print('Edges using raw edge_kind as semantic_type:')
for edge_kind, rel_type, count in results:
    print(f'  {edge_kind} + {rel_type}: {count}')

# Get total
cursor = conn.execute('SELECT COUNT(*) FROM edges WHERE semantic_type == edge_kind')
total_raw = cursor.fetchone()[0]
print(f'\nTotal raw fallbacks: {total_raw}')

# Check if these should be in the exact map or fallback map
print('\n=== Checking mapping coverage ===')

from agentic_core.adg.extraction.static_scanner import _SEMANTIC_TYPE_MAP, _SEMANTIC_FALLBACK

unmapped = []
for edge_kind, rel_type, count in results[:10]:  # Check top 10
    key = (edge_kind, rel_type)
    if key not in _SEMANTIC_TYPE_MAP and rel_type not in _SEMANTIC_FALLBACK:
        unmapped.append((edge_kind, rel_type, count))

if unmapped:
    print('Unmapped edge types:')
    for edge_kind, rel_type, count in unmapped:
        print(f'  {edge_kind} + {rel_type}: {count}')
else:
    print('Top 10 raw fallbacks are all mapped')

conn.close()
