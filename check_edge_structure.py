import sqlite3

conn = sqlite3.connect('artifacts/adg/adg_indexed_03242026_1825.sqlite')
cursor = conn.cursor()

cursor.execute('PRAGMA table_info(edges)')
columns = cursor.fetchall()
print('Edges table columns:')
for col in columns:
    print(f'  {col[1]} ({col[2]})')

# Get some examples of test coverage edges using proper column names
cursor.execute('SELECT src_id, dst_id FROM edges WHERE relation_type = "covers" LIMIT 5')
sample_covers = cursor.fetchall()
print('\nSample test coverage edges (by ID):')
for src_id, dst_id in sample_covers:
    # Get the actual names
    cursor.execute('SELECT adg_name FROM nodes WHERE id = ?', (src_id,))
    src_name = cursor.fetchone()[0]
    cursor.execute('SELECT adg_name FROM nodes WHERE id = ?', (dst_id,))
    dst_name = cursor.fetchone()[0]
    print(f'  {src_name} covers {dst_name}')

conn.close()
