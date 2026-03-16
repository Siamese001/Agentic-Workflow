import json
import sqlite3

DB = r"c:/Git/Agentic-Workflow/artifacts/adg/adg_indexed_03162026_0914.sqlite"

SQL_PACK = """
SELECT 'calls', COUNT(*) FROM edges WHERE relation_type='calls'
UNION ALL
SELECT 'records_execution_trace', COUNT(*) FROM edges WHERE relation_type='records_execution_trace'
UNION ALL
SELECT 'pulls_context', COUNT(*) FROM edges WHERE relation_type='pulls_context'
UNION ALL
SELECT 'emits_determinism_digest', COUNT(*) FROM edges WHERE relation_type='emits_determinism_digest'
UNION ALL
SELECT 'dispatches_healing_run', COUNT(*) FROM edges WHERE relation_type='dispatches_healing_run'
UNION ALL
SELECT 'agent_executes_agent', COUNT(*) FROM edges WHERE relation_type='agent_executes_agent'
UNION ALL
SELECT 'writes_through', COUNT(*) FROM edges WHERE relation_type='writes_through'
UNION ALL
SELECT 'writes_to', COUNT(*) FROM edges WHERE relation_type='writes_to'
UNION ALL
SELECT 'validated_by_safety_plane', COUNT(*) FROM edges WHERE relation_type='validated_by_safety_plane'
UNION ALL
SELECT 'applies_guardrail', COUNT(*) FROM edges WHERE relation_type='applies_guardrail'
UNION ALL
SELECT 'emits_metric_event', COUNT(*) FROM edges WHERE relation_type='emits_metric_event'
UNION ALL
SELECT 'emits_replay_key', COUNT(*) FROM edges WHERE relation_type='emits_replay_key'
UNION ALL
SELECT 'signs_execution_trace', COUNT(*) FROM edges WHERE relation_type='signs_execution_trace'
UNION ALL
SELECT 'reads_runtime_state', COUNT(*) FROM edges WHERE relation_type='reads_runtime_state'
UNION ALL
SELECT 'reads_env', COUNT(*) FROM edges WHERE relation_type='reads_env'
UNION ALL
SELECT 'invokes_eval', COUNT(*) FROM edges WHERE relation_type='invokes_eval';
"""

TARGETS = {"L0": 0.70, "L1": 0.70, "L2": 0.55, "L3": 1.00, "L4": 0.90, "L5": 1.00, "L6": 0.55}

def ratio(n, d):
    return 0.0 if d == 0 else n / d

with sqlite3.connect(DB) as conn:
    rows = conn.execute(SQL_PACK).fetchall()

counts = {k: v for k, v in rows}
ratios = {
    "L0": ratio(counts["records_execution_trace"], counts["calls"]),
    "L1": ratio(counts["pulls_context"], counts["records_execution_trace"]),
    "L2": ratio(counts["emits_determinism_digest"], counts["calls"]),
    "L3": ratio(counts["dispatches_healing_run"], counts["agent_executes_agent"]),
    "L4": ratio(counts["writes_through"], counts["writes_to"]),
    "L5": ratio(counts["validated_by_safety_plane"], counts["applies_guardrail"]),
    "L6": ratio(counts["emits_metric_event"], counts["calls"]),
}
completion = {k: min(ratios[k] / TARGETS[k], 1.0) for k in ratios}
overall = sum(completion.values()) / 7.0
print(json.dumps({"db": DB, "counts": counts, "ratios": ratios, "completion": completion, "overall": overall}, indent=2, sort_keys=True))
