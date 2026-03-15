"""RCA gap audit — verify current ADG edge counts vs ChatGPT feedback claims."""
import sqlite3
import glob

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
conn = sqlite3.connect(db)
c = conn.cursor()
print(f"DB: {db}\n")

NTEST = """
    AND source_file NOT LIKE '%test%'
    AND source_file NOT LIKE '%tests%'
    AND source_file NOT LIKE '%spec%'
    AND source_file NOT LIKE '%mock%'
    AND source_file NOT LIKE '%fixture%'
"""

def count_edges(rel, extra=""):
    r = conn.execute(
        f"SELECT COUNT(*) FROM edges WHERE relation_type=? {NTEST} {extra}", (rel,)
    ).fetchone()[0]
    return r

def count_sources(rel, extra=""):
    r = conn.execute(
        f"SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type=? {NTEST} {extra}", (rel,)
    ).fetchone()[0]
    return r

def count_exported(sym):
    r = conn.execute(
        f"SELECT COUNT(DISTINCT source_file) FROM edges WHERE symbol LIKE ? {NTEST}", (f"%{sym}%",)
    ).fetchone()[0]
    return r

print("=" * 70)
print("FEEDBACK-CLAIMED METRICS vs CURRENT ADG (non-test)")
print("=" * 70)

metrics = [
    # (label, relation_type, claimed, measure)
    ("routes_path",                    "routes_path",                 50,    "edges"),
    ("routes_through",                 "routes_through",              63,    "edges"),
    ("emits_replay_key",               "emits_replay_key",            14,    "sources"),
    ("emits_determinism_digest",       "emits_determinism_digest",    11,    "sources"),
    ("records_execution_trace",        "records_execution_trace",     85,    "sources"),
    ("applies_guardrail",              "applies_guardrail",           640,   "sources"),
    ("agent_executes_agent",           "agent_executes_agent",        3,     "sources"),
    ("reads_runtime_state",            "reads_runtime_state",         470,   "edges"),
    ("snapshots_state",                "snapshots_state",             2,     "sources"),
    ("reads_policy_state",             "reads_policy_state",          1340,  "edges"),
    ("signs_execution_trace",          "signs_execution_trace",       30,    "sources"),
    ("invokes_dynamic",                "invokes_dynamic",             540,   "edges"),
    ("invokes_getattr_dynamic",        "invokes_getattr_dynamic",     3000,  "edges"),
    ("proposal_commits_routing",       "proposal_commits_routing",    50,    "edges"),
    ("invokes_eval",                   "invokes_eval",                500,   "edges"),
    ("issues_capability_token",        "issues_capability_token",     0,     "sources"),
]

for label, rel, claimed, measure in metrics:
    if measure == "edges":
        actual = count_edges(rel)
    else:
        actual = count_sources(rel)
    delta = actual - claimed
    flag = "✓ IMPROVED" if delta > 0 else ("= SAME" if delta == 0 else "✗ REGRESSED")
    print(f"  {label:<40} claimed={claimed:5d}  actual={actual:5d}  delta={delta:+5d}  {flag}")

print()
print("=" * 70)
print("CI GATE SYMBOL EXPORTS (what the gates check)")
print("=" * 70)
for sym in [
    "ReasoningKnowledgeRecord", "capture_reasoning_pattern", "reasoning_pattern_reused",
    "ExecutionAdaptationRecord", "choose_execution_strategy",
    "CapabilityRegistry", "resolve_agent_for_capability", "CapabilityToken",
    "invoke_typed_tool", "ToolContract",
    "ReasoningEvaluationRubric", "evaluate_reasoning_step_from_trace",
    "create_reasoning_plan", "ReasoningPlan",
    "ExecutionObservabilityRecord", "record_execution_observability",
    "WorkflowVisualization", "StateLifecycleRecord", "HumanEscalation",
    "ObservabilityDashboard", "RoutingTelemetryRecord",
]:
    count = count_exported(sym)
    print(f"  symbol:{sym:<45} sources={count:4d}")

print()
print("=" * 70)
print("GAP: CI-gate symbols present but LOW CALL-SITE COVERAGE")
print("=" * 70)
# Check how many NEW modules are being called from production code
new_modules = [
    "reasoning_knowledge", "knowledge_orchestrator",
    "execution_adaptation", "adaptation_orchestrator",
    "reasoning_evaluation", "reasoning_chokepoint",
    "plan_creator", "reasoning_plan",
    "execution_observability", "observability_recorder",
    "workflow_visualization", "state_lifecycle",
    "human_escalation", "capability_registry",
]
for mod in new_modules:
    callers = conn.execute(
        f"SELECT COUNT(DISTINCT source_file) FROM edges WHERE (relation_type='calls' OR relation_type='invokes_dynamic') AND symbol LIKE ? {NTEST}",
        (f"%{mod}%",)
    ).fetchone()[0]
    print(f"  callers of {mod:<40} = {callers:4d}")

conn.close()
