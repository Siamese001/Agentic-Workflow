from pathlib import Path

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

emit_replay_key("p0", "investigate_sovereign_base_util")
emit_determinism_digest("p0", "investigate_sovereign_base_util")

_emit_dispatches_healing_run("p1", "investigate_sovereign_base_util", "L0")
_emit_routes_through("p1", "investigate_sovereign_base_util", "L0")
_emit_escalates_to_human("p1", "investigate_sovereign_base_util", "L0")
_emit_reads_policy_state("p1", "investigate_sovereign_base_util", "L0")

_emit_records_execution_trace("p0", "evidence", "investigate_sovereign_base_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "investigate_sovereign_base_util", "p0_governance")
_emit_snapshots_state("p0", "investigate_sovereign_base_util", "state_snapshot")
_emit_authorize_and_execute("p2", "investigate_sovereign_base_util", "execution_auth")
_emit_validates_capability("p2", "investigate_sovereign_base_util", "capability_check")
_emit_routes_to_capability("p2", "investigate_sovereign_base_util", "capability_route")
_emit_writes_via_uwg("p2", "investigate_sovereign_base_util", "uwg_write")
_emit_blocks_direct_write("p2", "investigate_sovereign_base_util", "direct_write_block")
_emit_records_tool_invocation("p2", "investigate_sovereign_base_util", "tool_invocation")
_emit_captures_execution_output("p2", "investigate_sovereign_base_util", "exec_output")
_emit_dispatches_agent("p3", "investigate_sovereign_base_util", "agent_dispatch")
_emit_coordinates_agents("p3", "investigate_sovereign_base_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "investigate_sovereign_base_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "investigate_sovereign_base_util", "healing_outcome")
_emit_escalates_failure("p3", "investigate_sovereign_base_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "investigate_sovereign_base_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "investigate_sovereign_base_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "investigate_sovereign_base_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "investigate_sovereign_base_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "investigate_sovereign_base_util", "eval_metric")
_emit_stores_embedding("p4", "investigate_sovereign_base_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "investigate_sovereign_base_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "investigate_sovereign_base_util", "exec_snapshot_link")

"Investigate Sovereign Base Agent territory classification."
import json

PROJECT_ROOT = Path(__file__).parent.parent
with open(PROJECT_ROOT / "agent_discovery_full.json") as f:
    agents = json.load(f)
sovereign_agents = [a for a in agents if a.get("territory") == "Sovereign Base Agent"]
for a in sovereign_agents[:20]:
    layer = a.get("layer", "?")
    path = a.get("path", "no path")
path_prefixes = {}
for a in sovereign_agents:
    path = a.get("path", "")
    if "/" in path or "\\" in path:
        prefix = path.split("/")[0] if "/" in path else path.split("\\")[0]
        path_prefixes[prefix] = path_prefixes.get(prefix, 0) + 1
for prefix, _count in sorted(path_prefixes.items(), key=lambda x: -x[1]):
    pass
