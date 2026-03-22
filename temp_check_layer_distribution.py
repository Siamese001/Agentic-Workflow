import sqlite3

conn = sqlite3.connect('artifacts/adg/adg_indexed_03222026_0839.sqlite')
cur = conn.cursor()

# Check layer distribution
cur.execute('SELECT layer, COUNT(*) FROM nodes WHERE entity_type="module" GROUP BY layer ORDER BY COUNT(*) DESC')
print('Module distribution by layer:')
total_modules = 0
for row in cur.fetchall():
    print(f'  {row[0]}: {row[1]}')
    total_modules += row[1]

print(f'\nTotal modules: {total_modules}')

# Check for new layer types
cur.execute('SELECT DISTINCT layer FROM nodes ORDER BY layer')
print('\nAll layer types:')
for row in cur.fetchall():
    print(f'  {row[0]}')

conn.close()
