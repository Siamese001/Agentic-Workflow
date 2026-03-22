import sqlite3

conn = sqlite3.connect('artifacts/adg/adg_indexed_03222026_0835.sqlite')
cur = conn.cursor()

cur.execute('SELECT value FROM meta WHERE key="commit_sha"')
row = cur.fetchone()
print('commit_sha:', row[0][:20] + '...' if row else 'NOT FOUND')

cur.execute('SELECT value FROM meta WHERE key="repo_state_hash"')
row = cur.fetchone()
print('repo_state_hash:', row[0][:20] + '...' if row else 'NOT FOUND')

conn.close()
