import sqlite3

conn = sqlite3.connect('artifacts/adg/adg_indexed_03242026_1825.sqlite')
cursor = conn.cursor()

cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print('Tables in ADG SQLite:')
for table in tables:
    print(f'  {table[0]}')

# Check if there's a nodes table instead of entities
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = [row[0] for row in cursor.fetchall()]
if 'nodes' in tables:
    cursor.execute('SELECT adg_name FROM nodes WHERE adg_name LIKE "%tests%" OR adg_name LIKE "%test%" LIMIT 10')
    test_nodes = cursor.fetchall()
    print('\nTest-related nodes in ADG:')
    for node in test_nodes:
        print(f'  {node[0]}')

    cursor.execute('SELECT COUNT(*) FROM nodes WHERE adg_name LIKE "%tests%" OR adg_name LIKE "%test%"')
    test_count = cursor.fetchone()[0]
    print(f'\nTotal test nodes: {test_count}')

conn.close()
