import sqlite3
import sys
from pathlib import Path

sys.path.append('tools')
from generate_full_adg import _infer_layer

# Check current L_UNKNOWN modules
sqlite_path = Path('artifacts/adg/adg_indexed_03222026_1252.sqlite')
conn = sqlite3.connect(sqlite_path)
cur = conn.cursor()

# Get total count and sample
cur.execute('SELECT COUNT(*) FROM nodes WHERE layer="L_UNKNOWN"')
total_count = cur.fetchone()[0]
print(f'Total L_UNKNOWN nodes: {total_count}')

# Get sample of resolved_paths
cur.execute('SELECT DISTINCT resolved_path FROM nodes WHERE layer="L_UNKNOWN" AND resolved_path IS NOT NULL LIMIT 20')
paths = [row[0] for row in cur.fetchall()]

print('\nSample L_UNKNOWN paths and their corrected layers:')
print('=' * 70)
for path in paths:
    corrected_layer = _infer_layer(path)
    status = '✅ FIXED' if corrected_layer != 'L_UNKNOWN' else '❌ STILL UNKNOWN'
    print(f'{status} {path:<55} -> {corrected_layer}')

conn.close()
