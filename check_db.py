import sqlite3

conn = sqlite3.connect('C:/Git/Agentic-Workflow/artifacts/adg/adg_indexed_03222026_1653.sqlite')
cur = conn.cursor()

cur.execute('SELECT relation_type, COUNT(*) FROM edges WHERE relation_type IN ("policy_verification", "dispatches_execution_plan", "mutation_signature", "parent_snapshot_hash")')
for r in cur.fetchall():
    print(f'{r[0]}: {r[1]}')

cur.execute('SELECT COUNT(*) FROM nodes WHERE entity_type IN ("test_suite", "test_case")')
print(f'Test nodes: {cur.fetchone()[0]}')

conn.close()
