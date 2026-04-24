import sqlite3
import glob
from agentic_core.L0_routing.config.path_constants import ADG_ARTIFACTS_DIR
f"{ADG_ARTIFACTS_DIR}/*.sqlite"
db = sorted(glob.glob(f"{ADG_ARTIFACTS_DIR}/*.sqlite"))[-1]
print("DB:", db)
con = sqlite3.connect(db)
cur = con.cursor()
cur.execute("PRAGMA table_info(edges)")
print([r[1] for r in cur.fetchall()])
con.close()
