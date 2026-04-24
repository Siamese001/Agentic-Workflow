import sqlite3
from agentic_core.L0_routing.config.path_constants import ADG_ARTIFACTS_DIR

for db in (
    f"{ADG_ARTIFACTS_DIR}/adg_indexed_04172026_0422.sqlite",
    f"{ADG_ARTIFACTS_DIR}/adg_indexed_04162026_2217.sqlite",
):
    c = sqlite3.connect(db)
    cur = c.cursor()
    cur.execute("SELECT COUNT(*) FROM violations WHERE severity='HIGH' AND category='antipattern'")
    raw = cur.fetchone()[0]
    cur.execute(
        "SELECT file_path, COUNT(*) n FROM violations "
        "WHERE severity='HIGH' AND category='antipattern' "
        "GROUP BY file_path ORDER BY n DESC LIMIT 10"
    )
    print(f"\n{db}")
    print(f"  raw HIGH antipattern count: {raw}")
    for f, n in cur.fetchall():
        print(f"    {n:4d}  {f}")
