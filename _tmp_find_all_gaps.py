"""Find all metrics below 100% and their gap modules."""
import sqlite3, glob, os

db_files = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"), key=os.path.getmtime)
db = db_files[-1]
print(f"Using: {db}")
conn = sqlite3.connect(db)

denom = conn.execute("SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type='calls'").fetchone()[0]
print(f"Denominator (modules_with_calls): {denom}\n")

# Get distinct module counts per relation_type
q = """
SELECT relation_type, COUNT(DISTINCT source_file) as module_count
FROM edges
GROUP BY relation_type
ORDER BY module_count ASC
"""
rows = conn.execute(q).fetchall()

# Show metrics below 100%
print("=== Metrics below 100% completion ===")
gaps = []
for rtype, cnt in rows:
    ratio = cnt / denom * 100
    if ratio < 100.0 and rtype not in ('imports', 'dead_imports', 'antipattern', 'violates',
        'reads_from', 'exports', 'decorated_by', 'reads_runtime_state', 'reads_env',
        'belongs_to_layer', 'implements', 'routes_through', 'instantiates',
        'uses_wall_clock', 'uses_uuid', 'invokes_getattr_dynamic', 'unreachable_after_raise',
        'accesses_credential', 'references_policy_hash', 'generates_prompt', 'routes_path',
        'invokes_importlib', 'reads_secret', 'reads_config', 'uses_random',
        'patches_time', 'enters_sandbox', 'grants_resource', 'external_http_call',
        'instruction_injection_source', 'invokes_dynamic', 'duplicate_method'):
        gaps.append((rtype, cnt, denom - cnt))
        print(f"  {rtype}: {cnt}/{denom} = {ratio:.2f}%  (gap={denom-cnt})")

# For the top gap metrics, find their missing modules
print(f"\n=== Gap module details for top metrics ===")
for rtype, cnt, gap in sorted(gaps, key=lambda x: x[2], reverse=True)[:8]:
    missing = conn.execute(f"""
        SELECT DISTINCT e1.source_file FROM edges e1
        WHERE e1.relation_type='calls'
        AND e1.source_file NOT IN (
            SELECT DISTINCT e2.source_file FROM edges e2
            WHERE e2.relation_type='{rtype}'
        )
        ORDER BY e1.source_file
        LIMIT 10
    """).fetchall()
    print(f"\n  {rtype} (gap={gap}):")
    for m in missing:
        print(f"    {m[0]}")

conn.close()
