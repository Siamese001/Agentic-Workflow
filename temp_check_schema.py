import sqlite3

conn = sqlite3.connect('artifacts/adg/adg_indexed_03222026_0837.sqlite')
cur = conn.cursor()

# Check edges table schema
cur.execute('PRAGMA table_info(edges)')
print('Edges table columns:')
for row in cur.fetchall():
    print(f'  {row[1]}')

conn.close()
