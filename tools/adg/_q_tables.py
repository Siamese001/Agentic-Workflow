import sqlite3
import glob

db = sorted(glob.glob("artifacts/adg/*.sqlite"))[-1]
print("DB:", db)
con = sqlite3.connect(db)
cur = con.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
print([r[0] for r in cur.fetchall()])
con.close()
