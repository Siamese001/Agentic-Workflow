import sqlite3

conn = sqlite3.connect('artifacts/adg/adg_indexed_03222026_0843.sqlite')
cur = conn.cursor()

# Check critical edge types
critical_edges = [
    'determinism_seed',
    'emits_determinism_digest',  # determinism_digest_emit
    'policy_verification',
    'authorize_and_execute',      # execution_authorization
    'dispatches_execution_plan', # execution_plan_dispatch
    'enters_sandbox',            # sandbox_entry
    'guardian_gate'
]

print('Critical edge type counts:')
for edge_type in critical_edges:
    cur.execute('SELECT COUNT(*) FROM edges WHERE relation_type=?', (edge_type,))
    count = cur.fetchone()[0]
    print(f'  {edge_type}: {count}')

conn.close()
