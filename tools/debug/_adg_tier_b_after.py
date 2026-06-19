import sqlite3
from pathlib import Path

DB = Path("artifacts/adg/adg_indexed_04232026_2248.sqlite")
c = sqlite3.connect(str(DB)).cursor()

targets = [
    "tools/eval/retrieval_benchmark.py",
    "ops_scripts/_archived_obsolete/dev_tools/L0_routing_scripts/_ssot_meta_learning.py",
    "agentic_core/L5_safety/reasoning/LocationHealerAgent.py",
    "agentic_core/L2_execution/utils/write_gateway.py",
]

for tgt in targets:
    rows = c.execute(
        "SELECT COUNT(*), disposition FROM violations WHERE file_path = ? "
        "AND category='antipattern' GROUP BY disposition",
        (tgt,),
    ).fetchall()
    print(f"{tgt}:")
    for n, d in rows:
        print(f"  {n:>4} {d}")

# Sample a few untriaged with edge_kind to see pattern
print("\n--- Sample untriaged antipatterns with edge_kind, paired with source line ---")
rows = c.execute(
    "SELECT v.file_path, v.line_no, e.edge_kind, substr(v.evidence,1,40) "
    "FROM violations v JOIN edges e ON v.edge_id=e.id "
    "WHERE v.category='antipattern' AND v.disposition='untriaged' "
    "AND e.edge_kind IN ('log_and_swallow','broad_exception_catch','silent_exception_swallow','return_none_swallow') "
    "LIMIT 15"
).fetchall()
for r in rows:
    fp, ln, ek, ev = r
    # Read the source line
    p = Path(fp)
    src_line = ""
    if p.exists():
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        if 1 <= ln <= len(lines):
            src_line = lines[ln - 1].strip()
    has_guard = "# review:" in src_line
    print(f"{fp}:{ln} kind={ek:<25} guard_inline={has_guard}")
    print(f"  src: {src_line[:110]}")
