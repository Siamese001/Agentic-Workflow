import sqlite3

conn = sqlite3.connect('artifacts/adg/adg_indexed_03222026_0839.sqlite')
cur = conn.cursor()

# Check edge type distribution
cur.execute('SELECT relation_type, COUNT(*) FROM edges GROUP BY relation_type ORDER BY COUNT(*) DESC')
print('Edge distribution by type:')
total_edges = 0
for row in cur.fetchall():
    print(f'  {row[0]}: {row[1]}')
    total_edges += row[1]

print(f'\nTotal edges: {total_edges}')

conn.close()
