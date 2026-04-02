import sqlite3
import sys
from pathlib import Path

sys.path.append('tools')
from generate_full_adg import _infer_layer

# Check current L_UNKNOWN modules
sqlite_path = Path('artifacts/adg/adg_indexed_03222026_1252.sqlite')
conn = sqlite3.connect(sqlite_path)
cur = conn.cursor()

cur.execute('SELECT resolved_path FROM nodes WHERE layer="L_UNKNOWN"')
unknown_paths = [row[0] for row in cur.fetchall()]

print('Current L_UNKNOWN modules and their corrected layers:')
print('=' * 60)
for path in unknown_paths:
    corrected_layer = _infer_layer(path)
    status = '✅ FIXED' if corrected_layer != 'L_UNKNOWN' else '❌ STILL UNKNOWN'
    print(f'{status} {path:<50} -> {corrected_layer}')

conn.close()
