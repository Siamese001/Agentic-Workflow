import json
import sqlite3

DB = r"c:/Git/Agentic-Workflow/artifacts/adg/adg_indexed_03162026_0931.sqlite"

TARGETS = {"L0": 0.70, "L1": 0.70, "L2": 0.55, "L3": 1.00, "L4": 0.90, "L5": 1.00, "L6": 0.55}

SQL_COUNTS = """
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
SELECT 'emits_metric_event', COUNT(*) FROM edges WHERE relation_type='emits_metric_event';
"""

def ratio(n,d):
    return 0.0 if d==0 else n/d

with sqlite3.connect(DB) as con:
    counts = dict(con.execute(SQL_COUNTS).fetchall())

ratios = {
    "L0": ratio(counts["records_execution_trace"], counts["calls"]),
    "L1": ratio(counts["pulls_context"], counts["records_execution_trace"]),
    "L2": ratio(counts["emits_determinism_digest"], counts["calls"]),
    "L3": ratio(counts["dispatches_healing_run"], counts["agent_executes_agent"]),
    "L4": ratio(counts["writes_through"], counts["writes_to"]),
    "L5": ratio(counts["validated_by_safety_plane"], counts["applies_guardrail"]),
    "L6": ratio(counts["emits_metric_event"], counts["calls"]),
}
completion = {k: min(ratios[k]/TARGETS[k],1.0) for k in ratios}
print(json.dumps({"db":DB,"counts":counts,"ratios":ratios,"completion":completion}, indent=2, sort_keys=True))
