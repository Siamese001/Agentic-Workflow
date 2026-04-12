"""Check if new stubs are in ADG and producing coverage edges."""

import glob
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

db = sorted(glob.glob(str(PROJECT_ROOT / "artifacts/adg/adg_indexed_*.sqlite")))[-1]
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row

# Check a sample of the newly generated stubs
sample_stubs = [
    "tests/unit/agentic_core/adg/extraction/test_static_scanner_adg.py",
    "tests/unit/agentic_core/cache/test_redis_cache_client_adg.py",
    "tests/unit/agentic_core/evaluation/judges/test_llm_judge_adg.py",
    "tests/unit/agentic_core/interfaces/test_IBlackboardLeaseVerifierProtocol_adg.py",
    "tests/unit/agentic_core/mixins/test_atomic_execution_mixin_adg.py",
    "tests/unit/agentic_core/patterns/test_base_adg.py",
    "tests/unit/agentic_core/runtime/test_tools_adg.py",
]

print("Checking if new stubs are in ADG nodes table:")
for stub in sample_stubs:
    row = conn.execute("SELECT id, resolved_path FROM nodes WHERE resolved_path=?", (stub,)).fetchone()
    if row:
        # Check if it has imports edges
        edges = conn.execute(
            "SELECT COUNT(*) as cnt FROM edges e WHERE e.src_id=? AND e.relation_type='imports'",
            (row["id"],),
        ).fetchone()
        print(f"  FOUND: {stub} -> {edges['cnt']} imports edges")
    else:
        print(f"  MISSING from ADG: {stub}")

# Total stub coverage
total_stubs = conn.execute(
    "SELECT COUNT(DISTINCT n1.resolved_path) as cnt "
    "FROM edges e JOIN nodes n1 ON e.src_id=n1.id "
    "WHERE e.relation_type='imports' "
    "AND n1.resolved_path LIKE 'tests/%' "
    "AND n1.resolved_path LIKE '%_adg.py'",
).fetchone()
print(f"\nTotal _adg files with imports edges in ADG: {total_stubs['cnt']}")

# Coverage after new stubs
src_mods = conn.execute(
    "SELECT COUNT(*) as cnt FROM nodes "
    "WHERE entity_type='module' "
    "AND resolved_path LIKE 'agentic_core/%' "
    "AND resolved_path NOT LIKE '%__pycache__%'",
).fetchone()
covered = conn.execute(
    "SELECT COUNT(DISTINCT n2.resolved_path) as cnt "
    "FROM edges e "
    "JOIN nodes n1 ON e.src_id=n1.id "
    "JOIN nodes n2 ON e.dst_id=n2.id "
    "WHERE e.relation_type='imports' "
    "AND n1.resolved_path LIKE 'tests/%' "
    "AND n2.resolved_path LIKE 'agentic_core/%' "
    "AND n2.resolved_path NOT LIKE '%__pycache__%'",
).fetchone()
total = src_mods["cnt"]
cov = covered["cnt"]
print(f"\nCoverage: {cov}/{total} = {100 * cov / total:.1f}%")

conn.close()


def check_coverage():
    return {}
