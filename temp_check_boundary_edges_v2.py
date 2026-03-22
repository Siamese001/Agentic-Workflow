import sqlite3

conn = sqlite3.connect('artifacts/adg/adg_indexed_03222026_0837.sqlite')
cur = conn.cursor()

# Check internal edges
cur.execute('''
SELECT DISTINCT n.adg_name
FROM edges e
JOIN nodes n ON e.dst_id = n.id
WHERE e.relation_type="imports" AND e.edge_kind="internal"
LIMIT 10
''')
print('Sample internal imports:')
for row in cur.fetchall():
    print(f'  {row[0]}')

# Check external edges
cur.execute('''
SELECT DISTINCT n.adg_name
FROM edges e
JOIN nodes n ON e.dst_id = n.id
WHERE e.relation_type="imports" AND e.edge_kind="external"
LIMIT 10
''')
print('\nSample external imports:')
for row in cur.fetchall():
    print(f'  {row[0]}')

conn.close()
