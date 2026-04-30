import sqlite3
from pathlib import Path
snap = sorted(p for p in Path("artifacts/adg").glob("adg_indexed_*.sqlite") if "99999999" not in p.name)[-1]
con = sqlite3.connect(snap); cur = con.cursor()

target = "agentic_core/L6_observability/utils/integrity_report_generator_util.py"
print(f"\n=== {target} L6->lower imports ===")
cur.execute("""
    SELECT nd.resolved_path, e.line_no, e.symbol
    FROM edges e
    JOIN nodes nd ON nd.id = e.dst_id
    WHERE e.relation_type = 'imports'
      AND e.source_file = ?
      AND nd.resolved_path LIKE 'agentic_core/L%'
      AND nd.resolved_path NOT LIKE 'agentic_core/L6_observability/%'
    ORDER BY e.line_no
""", (target,))
for r in cur.fetchall():
    print(f"  L{r[1]:>4}: {r[0]:60} -> {r[2]}")

target = "agentic_core/L6_observability/utils/evaluation/golden/__init__.py"
print(f"\n=== {target} L6->lower imports ===")
cur.execute("""
    SELECT nd.resolved_path, e.line_no, e.symbol
    FROM edges e JOIN nodes nd ON nd.id = e.dst_id
    WHERE e.relation_type = 'imports' AND e.source_file = ?
      AND nd.resolved_path LIKE 'agentic_core/L%'
      AND nd.resolved_path NOT LIKE 'agentic_core/L6_observability/%'
    ORDER BY e.line_no
""", (target,))
for r in cur.fetchall():
    print(f"  L{r[1]:>4}: {r[0]:60} -> {r[2]}")
