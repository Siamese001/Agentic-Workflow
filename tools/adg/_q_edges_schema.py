import sqlite3
import glob

db = sorted(glob.glob("artifacts/adg/*.sqlite"))[-1]
print("DB:", db)
con = sqlite3.connect(db)
cur = con.cursor()
cur.execute("PRAGMA table_info(edges)")
print([r[1] for r in cur.fetchall()])
con.close()
