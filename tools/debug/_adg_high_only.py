import sqlite3
c = sqlite3.connect('artifacts/adg/adg_indexed_04232026_2248.sqlite').cursor()
cols = [d[0] for d in c.execute('SELECT * FROM violations LIMIT 0').description]
rows = c.execute("SELECT * FROM violations WHERE severity='HIGH'").fetchall()
print(f"HIGH count: {len(rows)}")
for r in rows:
    d = dict(zip(cols, r))
    print("---")
    for k, v in d.items():
        print(f"  {k}: {v}")
