"""Select wave targets for L4 memory authority hardening."""

import pathlib
import sqlite3
import sys

db_dir = pathlib.Path(r"C:\Git\Agentic-Workflow\artifacts\adg")
dbs = sorted(db_dir.glob("adg_indexed_*.sqlite"))
db = dbs[-1]
print(f"Using: {db.name}")
conn = sqlite3.connect(str(db))

wave = int(sys.argv[1]) if len(sys.argv) > 1 else 1

# Wave 1: apps_* filesystem persistence — highest writes_to, file-related modules
# We want modules that have writes_to edges but few writes_through edges
# and are filesystem-related (file save, report export, JSON/YAML emitters)

if wave == 1:
    scope = "apps_%"
    print(f"\n=== WAVE {wave}: {scope} filesystem persistence modules ===")
    rows = conn.execute(
        """
        SELECT e.source_file,
               SUM(CASE WHEN e.relation_type='writes_to' THEN 1 ELSE 0 END) as wt,
               SUM(CASE WHEN e.relation_type='writes_through' THEN 1 ELSE 0 END) as wth
        FROM edges e
        WHERE e.relation_type IN ('writes_to','writes_through')
          AND e.source_file LIKE ?
          AND e.source_file NOT LIKE 'tests/%'
        GROUP BY e.source_file
        HAVING wt > 0
        ORDER BY (wt - wth) DESC
        LIMIT 30
    """,
        (scope,),
    ).fetchall()

    print(f"{'Module':<70} {'writes_to':>10} {'writes_through':>15} {'gap':>6}")
    print("-" * 105)
    for sf, wt, wth in rows:
        print(f"  {sf:<68} {wt:>10} {wth:>15} {wt - wth:>6}")

elif wave == 2:
    # Wave 2-5 etc - show all apps_* grouped
    for prefix in [
        "apps_shared",
        "apps_rg",
        "apps_lic",
        "apps_eval",
        "apps_exec",
        "apps_rfp",
        "apps_research",
    ]:
        rows = conn.execute(
            """
            SELECT e.source_file,
                   SUM(CASE WHEN e.relation_type='writes_to' THEN 1 ELSE 0 END) as wt,
                   SUM(CASE WHEN e.relation_type='writes_through' THEN 1 ELSE 0 END) as wth
            FROM edges e
            WHERE e.relation_type IN ('writes_to','writes_through')
              AND e.source_file LIKE ?
              AND e.source_file NOT LIKE 'tests/%'
            GROUP BY e.source_file
            HAVING wt > wth + 1
            ORDER BY (wt - wth) DESC
            LIMIT 20
        """,
            (prefix + "%",),
        ).fetchall()
        if rows:
            total_gap = sum(wt - wth for _, wt, wth in rows)
            print(f"\n--- {prefix} (total gap: {total_gap}) ---")
            for sf, wt, wth in rows:
                print(f"  {sf}: writes_to={wt}, writes_through={wth}, gap={wt - wth}")

conn.close()
