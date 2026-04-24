import sqlite3
import glob
from agentic_core.L0_routing.config.path_constants import ADG_ARTIFACTS_DIR

db = sorted(glob.glob(f"{ADG_ARTIFACTS_DIR}/*.sqlite"))[-1]
print("DB:", db)
con = sqlite3.connect(db)
cur = con.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
print([r[0] for r in cur.fetchall()])
con.close()
