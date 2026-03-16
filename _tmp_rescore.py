"""Re-score all metrics after wave wiring."""
import sqlite3, glob, os

db_files = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"), key=os.path.getmtime)
db = db_files[-1]
print(f"Using: {db}")
conn = sqlite3.connect(db)

denom = conn.execute("SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type='calls'").fetchone()[0]
print(f"Denominator (modules_with_calls): {denom}\n")

# Get all relation_type distinct module counts
rows = conn.execute("""
    SELECT relation_type, COUNT(DISTINCT source_file) as cnt
    FROM edges
    GROUP BY relation_type
    ORDER BY cnt DESC
""").fetchall()

# Categorize metrics
SKIP = {'imports', 'dead_imports', 'antipattern', 'violates', 'reads_from', 'exports',
        'decorated_by', 'reads_runtime_state', 'reads_env', 'belongs_to_layer',
        'implements', 'routes_through', 'instantiates', 'uses_wall_clock', 'uses_uuid',
        'invokes_getattr_dynamic', 'unreachable_after_raise', 'accesses_credential',
        'references_policy_hash', 'generates_prompt', 'routes_path', 'invokes_importlib',
        'reads_secret', 'reads_config', 'uses_random', 'patches_time', 'enters_sandbox',
        'grants_resource', 'external_http_call', 'instruction_injection_source',
        'invokes_dynamic', 'duplicate_method'}

print("=" * 80)
print(f"{'METRIC':<45} {'COUNT':>6} {'DENOM':>6} {'RATIO':>8} {'STATUS'}")
print("=" * 80)

at_100 = 0
near_100 = 0
below = 0

for rtype, cnt in rows:
    if rtype in SKIP:
        continue
    ratio = cnt / denom * 100
    if ratio >= 100.0:
        status = "✅ 100%"
        at_100 += 1
    elif ratio >= 99.5:
        status = "🟡 near"
        near_100 += 1
    else:
        status = f"❌ gap={denom - cnt}"
        below += 1
    print(f"  {rtype:<43} {cnt:>6} {denom:>6} {ratio:>7.2f}% {status}")

print("=" * 80)
print(f"Summary: {at_100} at 100%, {near_100} near 100%, {below} below 99.5%")
print(f"Total tracked metrics: {at_100 + near_100 + below}")

# Show the specific gap metrics that were targeted this wave
print("\n--- Wave targets ---")
wave_metrics = [
    'captures_pattern', 'captures_runtime_anomaly', 'feeds_meta_learning',
    'improves_agent_policy', 'links_incident_trace', 'records_incident_event',
    'records_learning_event', 'stores_learning_state', 'triggers_alert',
    'updates_monitoring_state', 'updates_routing_strategy', 'writes_learning_snapshot',
    'writes_observability_log',
    'applies_guardrail', 'authorize_and_execute', 'blocks_direct_write',
    'captures_evaluation_metric', 'captures_execution_output', 'coordinates_agents',
    'dispatches_agent', 'dispatches_healing_run', 'escalates_failure',
    'invokes_evaluation', 'links_execution_to_snapshot', 'orchestrates_workflow',
    'records_healing_outcome', 'records_telemetry_event', 'records_tool_invocation',
    'records_workflow_lineage', 'routes_to_capability', 'signs_execution_trace',
    'snapshots_state', 'updates_meta_learning_state', 'validates_capability',
    'writes_via_uwg', 'stores_embedding', 'emits_metric_event',
    'escalates_to_human',
]
for m in wave_metrics:
    cnt = conn.execute(f"SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type=?", (m,)).fetchone()[0]
    ratio = cnt / denom * 100
    print(f"  {m:<45} {cnt:>6}/{denom} = {ratio:.2f}%")

conn.close()
