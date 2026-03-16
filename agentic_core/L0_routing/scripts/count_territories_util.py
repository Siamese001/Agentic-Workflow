import re
from collections import Counter

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "count_territories_util")
emit_determinism_digest("p0", "count_territories_util")

_emit_dispatches_healing_run("p1", "count_territories_util", "L0")
_emit_routes_through("p1", "count_territories_util", "L0")
_emit_escalates_to_human("p1", "count_territories_util", "L0")
_emit_reads_policy_state("p1", "count_territories_util", "L0")

_emit_records_execution_trace("p0", "evidence", "count_territories_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "count_territories_util", "p0_governance")
_emit_snapshots_state("p0", "count_territories_util", "state_snapshot")
_emit_authorize_and_execute("p2", "count_territories_util", "execution_auth")
_emit_validates_capability("p2", "count_territories_util", "capability_check")
_emit_routes_to_capability("p2", "count_territories_util", "capability_route")
_emit_writes_via_uwg("p2", "count_territories_util", "uwg_write")
_emit_blocks_direct_write("p2", "count_territories_util", "direct_write_block")
_emit_records_tool_invocation("p2", "count_territories_util", "tool_invocation")
_emit_captures_execution_output("p2", "count_territories_util", "exec_output")
_emit_dispatches_agent("p3", "count_territories_util", "agent_dispatch")
_emit_coordinates_agents("p3", "count_territories_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "count_territories_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "count_territories_util", "healing_outcome")
_emit_escalates_failure("p3", "count_territories_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "count_territories_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "count_territories_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "count_territories_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "count_territories_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "count_territories_util", "eval_metric")
_emit_stores_embedding("p4", "count_territories_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "count_territories_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "count_territories_util", "exec_snapshot_link")

pat = re.compile('"Territory":\\s*"([^"]+)",\\s*"Total":\\s*(\\d+)')
counts = Counter()
with open("agentic_core/L6_observability/dashboards/autonomy_dashboard.html", encoding="utf-8") as f:
    for line in f:
        for m in pat.finditer(line):
            territory = m.group(1)
            count = int(m.group(2))
            counts[territory] += count
print("Territory Agent Counts:")
print("=" * 60)
for territory, cnt in counts.most_common(35):
    print(f"{territory:45} {cnt:>4}")
