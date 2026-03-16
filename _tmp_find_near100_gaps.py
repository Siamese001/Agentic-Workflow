"""Find exact gap modules for near-100% metrics."""
import sqlite3, glob, os

db_files = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"), key=os.path.getmtime)
db = db_files[-1]
conn = sqlite3.connect(db)

denom = conn.execute("SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type='calls'").fetchone()[0]

# Group 1: gap=6 metrics (99.80%)
gap6_metrics = [
    'captures_pattern', 'captures_runtime_anomaly', 'feeds_meta_learning',
    'improves_agent_policy', 'links_incident_trace', 'records_incident_event',
    'records_learning_event', 'stores_learning_state', 'triggers_alert',
    'updates_monitoring_state', 'updates_routing_strategy', 'writes_learning_snapshot',
    'writes_observability_log'
]

print("=== Gap-6 modules (shared across 13 metrics at 99.80%) ===")
missing6 = conn.execute(f"""
    SELECT DISTINCT e1.source_file FROM edges e1
    WHERE e1.relation_type='calls'
    AND e1.source_file NOT IN (
        SELECT DISTINCT e2.source_file FROM edges e2
        WHERE e2.relation_type='captures_pattern'
    )
    ORDER BY e1.source_file
""").fetchall()
for m in missing6:
    print(f"  {m[0]}")

# Group 2: gap=5 metrics (99.83%)
gap5_metrics = [
    'applies_guardrail', 'authorize_and_execute', 'blocks_direct_write',
    'captures_evaluation_metric', 'captures_execution_output', 'coordinates_agents',
    'dispatches_agent', 'dispatches_healing_run', 'escalates_failure',
    'invokes_evaluation', 'links_execution_to_snapshot', 'orchestrates_workflow',
    'records_healing_outcome', 'records_telemetry_event', 'records_tool_invocation',
    'records_workflow_lineage', 'routes_to_capability', 'signs_execution_trace',
    'snapshots_state', 'updates_meta_learning_state', 'validates_capability',
    'writes_via_uwg'
]

print(f"\n=== Gap-5 modules (shared across 22 metrics at 99.83%) ===")
missing5 = conn.execute(f"""
    SELECT DISTINCT e1.source_file FROM edges e1
    WHERE e1.relation_type='calls'
    AND e1.source_file NOT IN (
        SELECT DISTINCT e2.source_file FROM edges e2
        WHERE e2.relation_type='applies_guardrail'
    )
    ORDER BY e1.source_file
""").fetchall()
for m in missing5:
    print(f"  {m[0]}")

# Group 3: gap=4 (stores_embedding at 99.87%)
print(f"\n=== Gap-4 modules (stores_embedding at 99.87%) ===")
missing4 = conn.execute(f"""
    SELECT DISTINCT e1.source_file FROM edges e1
    WHERE e1.relation_type='calls'
    AND e1.source_file NOT IN (
        SELECT DISTINCT e2.source_file FROM edges e2
        WHERE e2.relation_type='stores_embedding'
    )
    ORDER BY e1.source_file
""").fetchall()
for m in missing4:
    print(f"  {m[0]}")

# Unique union of all gap modules
all_gap = set(m[0] for m in missing6) | set(m[0] for m in missing5) | set(m[0] for m in missing4)
print(f"\n=== Total unique gap modules: {len(all_gap)} ===")
for m in sorted(all_gap):
    print(f"  {m}")

conn.close()
