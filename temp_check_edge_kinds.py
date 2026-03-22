import sqlite3

conn = sqlite3.connect('artifacts/adg/adg_indexed_03222026_0837.sqlite')
cur = conn.cursor()

# Check import edge kinds
cur.execute('SELECT DISTINCT edge_kind FROM edges WHERE relation_type="imports" ORDER BY edge_kind')
print('Import edge kinds:')
for row in cur.fetchall():
    print(f'  {row[0]}')

# Count each edge kind for imports
cur.execute('SELECT edge_kind, COUNT(*) FROM edges WHERE relation_type="imports" GROUP BY edge_kind ORDER BY edge_kind')
print('\nImport edge counts:')
for row in cur.fetchall():
    print(f'  {row[0]}: {row[1]}')

conn.close()
