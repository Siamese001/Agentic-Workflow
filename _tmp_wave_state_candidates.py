import json
import sqlite3

DB = r"c:/Git/Agentic-Workflow/artifacts/adg/adg_indexed_03162026_1039.sqlite"

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

WAVE_QUERIES = {
    "L0": """
        WITH den AS (SELECT DISTINCT source_file FROM edges WHERE relation_type='calls'),
             num AS (SELECT DISTINCT source_file FROM edges WHERE relation_type='records_execution_trace')
        SELECT d.source_file, COUNT(*) AS centrality
        FROM den d JOIN edges e ON e.source_file=d.source_file AND e.relation_type='calls'
        LEFT JOIN num n ON n.source_file=d.source_file
        WHERE n.source_file IS NULL
        GROUP BY d.source_file
        ORDER BY centrality DESC
        LIMIT 15;
    """,
    "L1": """
        WITH den AS (SELECT DISTINCT source_file FROM edges WHERE relation_type='records_execution_trace'),
             num AS (SELECT DISTINCT source_file FROM edges WHERE relation_type='pulls_context')
        SELECT d.source_file, COUNT(*) AS centrality
        FROM den d JOIN edges e ON e.source_file=d.source_file AND e.relation_type='records_execution_trace'
        LEFT JOIN num n ON n.source_file=d.source_file
        WHERE n.source_file IS NULL
        GROUP BY d.source_file
        ORDER BY centrality DESC
        LIMIT 15;
    """,
    "L2": """
        WITH den AS (SELECT DISTINCT source_file FROM edges WHERE relation_type='calls'),
             num AS (SELECT DISTINCT source_file FROM edges WHERE relation_type='emits_determinism_digest')
        SELECT d.source_file, COUNT(*) AS centrality
        FROM den d JOIN edges e ON e.source_file=d.source_file AND e.relation_type='calls'
        LEFT JOIN num n ON n.source_file=d.source_file
        WHERE n.source_file IS NULL
        GROUP BY d.source_file
        ORDER BY centrality DESC
        LIMIT 15;
    """,
    "L3": """
        WITH den AS (SELECT DISTINCT source_file FROM edges WHERE relation_type='agent_executes_agent'),
             num AS (SELECT DISTINCT source_file FROM edges WHERE relation_type='dispatches_healing_run')
        SELECT d.source_file, COUNT(*) AS centrality
        FROM den d JOIN edges e ON e.source_file=d.source_file AND e.relation_type='agent_executes_agent'
        LEFT JOIN num n ON n.source_file=d.source_file
        WHERE n.source_file IS NULL
        GROUP BY d.source_file
        ORDER BY centrality DESC
        LIMIT 15;
    """,
    "L4": """
        WITH den AS (SELECT DISTINCT source_file FROM edges WHERE relation_type='writes_to'),
             num AS (SELECT DISTINCT source_file FROM edges WHERE relation_type='writes_through')
        SELECT d.source_file, COUNT(*) AS centrality
        FROM den d JOIN edges e ON e.source_file=d.source_file AND e.relation_type='writes_to'
        LEFT JOIN num n ON n.source_file=d.source_file
        WHERE n.source_file IS NULL
        GROUP BY d.source_file
        ORDER BY centrality DESC
        LIMIT 15;
    """,
    "L5": """
        WITH den AS (SELECT DISTINCT source_file FROM edges WHERE relation_type='applies_guardrail'),
             num AS (SELECT DISTINCT source_file FROM edges WHERE relation_type='validated_by_safety_plane')
        SELECT d.source_file, COUNT(*) AS centrality
        FROM den d JOIN edges e ON e.source_file=d.source_file AND e.relation_type='applies_guardrail'
        LEFT JOIN num n ON n.source_file=d.source_file
        WHERE n.source_file IS NULL
        GROUP BY d.source_file
        ORDER BY centrality DESC
        LIMIT 15;
    """,
    "L6": """
        WITH den AS (SELECT DISTINCT source_file FROM edges WHERE relation_type='calls'),
             num AS (SELECT DISTINCT source_file FROM edges WHERE relation_type='emits_metric_event')
        SELECT d.source_file, COUNT(*) AS centrality
        FROM den d JOIN edges e ON e.source_file=d.source_file AND e.relation_type='calls'
        LEFT JOIN num n ON n.source_file=d.source_file
        WHERE n.source_file IS NULL
        GROUP BY d.source_file
        ORDER BY centrality DESC
        LIMIT 15;
    """,
}

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

def delta_to_target(k):
    return max(TARGETS[k]-ratios[k], 0.0)

order_pref = {"L2":0,"L0":1,"L6":2,"L1":3,"L4":4,"L5":5,"L3":6}
ranked = sorted(completion, key=lambda k: (completion[k], -delta_to_target(k), order_pref[k]))

with sqlite3.connect(DB) as con:
    candidates = {k: con.execute(WAVE_QUERIES[k]).fetchall() for k in ranked}

chosen = None
for k in ranked:
    if candidates[k]:
        chosen = k
        break

print(json.dumps({
    "db": DB,
    "counts": counts,
    "ratios": ratios,
    "completion": completion,
    "ranked": ranked,
    "candidate_counts": {k: len(v) for k,v in candidates.items()},
    "chosen": chosen,
    "chosen_candidates": candidates.get(chosen, []),
}, indent=2, sort_keys=True))
