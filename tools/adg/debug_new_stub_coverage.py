"""Debug: check if new stubs actually have imports edges to uncovered src modules."""

import glob
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

db = sorted(glob.glob(str(PROJECT_ROOT / "artifacts/adg/adg_indexed_*.sqlite")))[-1]
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row

# Check what src modules the new stubs cover
sample_stubs = [
    "tests/unit/agentic_core/adg/extraction/test_static_scanner_adg.py",
    "tests/unit/agentic_core/cache/test_redis_cache_client_adg.py",
    "tests/unit/agentic_core/evaluation/judges/test_llm_judge_adg.py",
    "tests/unit/agentic_core/runtime/test_tools_adg.py",
    "tests/unit/agentic_core/patterns/test_base_adg.py",
]

for stub in sample_stubs:
    row = conn.execute("SELECT id FROM nodes WHERE resolved_path=?", (stub,)).fetchone()
    if not row:
        print(f"MISSING: {stub}")
        continue
    edges = list(
        conn.execute(
            "SELECT n2.resolved_path as dst "
            "FROM edges e JOIN nodes n2 ON e.dst_id=n2.id "
            "WHERE e.src_id=? AND e.relation_type='imports' "
            "AND n2.resolved_path LIKE 'agentic_core/%'",
            (row["id"],),
        ),
    )
    print(f"\n{stub}:")
    for e in edges:
        print(f"  -> {e['dst']}")

# Key question: how many NEW src modules do the 289 stubs cover
# that weren't covered before?
all_test_files_now = {
    r["resolved_path"]
    for r in conn.execute(
        "SELECT DISTINCT n1.resolved_path "
        "FROM edges e JOIN nodes n1 ON e.src_id=n1.id "
        "WHERE e.relation_type='imports' "
        "AND n1.resolved_path LIKE 'tests/%'",
    )
}
non_adg = [f for f in all_test_files_now if not Path(f).stem.endswith("_adg")]
adg = [f for f in all_test_files_now if Path(f).stem.endswith("_adg")]
print(f"\nTotal test files with any imports edge: {len(all_test_files_now)}")
print(f"  ADG stubs: {len(adg)}")
print(f"  Non-ADG: {len(non_adg)}")

# Src modules covered ONLY by non-adg tests
non_adg_covered = set()
for f in non_adg:
    row = conn.execute("SELECT id FROM nodes WHERE resolved_path=?", (f,)).fetchone()
    if row:
        for e in conn.execute(
            "SELECT n2.resolved_path FROM edges e JOIN nodes n2 ON e.dst_id=n2.id "
            "WHERE e.src_id=? AND e.relation_type='imports' "
            "AND n2.resolved_path LIKE 'agentic_core/%'",
            (row["id"],),
        ):
            non_adg_covered.add(e[0].split("::")[0])

print(f"\nSrc modules covered by behavioral (non-ADG) tests: {len(non_adg_covered)}")

conn.close()
