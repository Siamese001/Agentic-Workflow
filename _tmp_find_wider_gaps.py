"""Find gap modules for 98.8% tier metrics to get 12+ total files."""
import sqlite3, glob, os

db_files = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"), key=os.path.getmtime)
db = db_files[-1]
conn = sqlite3.connect(db)

# Gap modules for writes_through (gap=34)
print("=== writes_through gap modules (gap=34) ===")
missing_wt = conn.execute("""
    SELECT DISTINCT e1.source_file FROM edges e1
    WHERE e1.relation_type='calls'
    AND e1.source_file NOT IN (
        SELECT DISTINCT e2.source_file FROM edges e2
        WHERE e2.relation_type='writes_through'
    )
    ORDER BY e1.source_file
""").fetchall()
for m in missing_wt:
    print(f"  {m[0]}")

# Gap modules for pulls_context (gap=35)
print(f"\n=== pulls_context gap modules (gap=35) ===")
missing_pc = conn.execute("""
    SELECT DISTINCT e1.source_file FROM edges e1
    WHERE e1.relation_type='calls'
    AND e1.source_file NOT IN (
        SELECT DISTINCT e2.source_file FROM edges e2
        WHERE e2.relation_type='pulls_context'
    )
    ORDER BY e1.source_file
""").fetchall()
for m in missing_pc:
    print(f"  {m[0]}")

# Gap modules for execution_terminates_at_uwg (gap=36)
print(f"\n=== execution_terminates_at_uwg gap modules (gap=36) ===")
missing_uwg = conn.execute("""
    SELECT DISTINCT e1.source_file FROM edges e1
    WHERE e1.relation_type='calls'
    AND e1.source_file NOT IN (
        SELECT DISTINCT e2.source_file FROM edges e2
        WHERE e2.relation_type='execution_terminates_at_uwg'
    )
    ORDER BY e1.source_file
""").fetchall()
for m in missing_uwg:
    print(f"  {m[0]}")

# Which of these are NOT in the 6 already patched?
already = {
    'apps_shared/utils/rank_observability_components_util.py',
    'system_learning/engines/historical_backfill_engine.py',
    'tests/system_learning/test_healing_backups_rca_waves.py',
    'tests/system_learning/test_historical_backfill_engine.py',
    'tests/system_learning/test_sl_gap_fixes.py',
    'tests/unit/system_learning/engines/test_cross_repo_system_learning_import.py',
}
all_new = set(m[0] for m in missing_wt) | set(m[0] for m in missing_pc) | set(m[0] for m in missing_uwg)
additional = sorted(all_new - already)
print(f"\n=== Additional modules beyond already-patched 6 ({len(additional)}) ===")
for m in additional:
    print(f"  {m}")

conn.close()
