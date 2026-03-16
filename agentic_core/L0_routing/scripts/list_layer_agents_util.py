"""
List agents by layer for batch hardening.

Reads from agent_discovery_full.json - run full_agent_discovery.py first.
"""

import json
import sys

from agentic_core.L0_routing.config import AGENT_DISCOVERY_JSON
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

emit_replay_key("p0", "list_layer_agents_util")
emit_determinism_digest("p0", "list_layer_agents_util")

_emit_dispatches_healing_run("p1", "list_layer_agents_util", "L0")
_emit_routes_through("p1", "list_layer_agents_util", "L0")
_emit_escalates_to_human("p1", "list_layer_agents_util", "L0")
_emit_reads_policy_state("p1", "list_layer_agents_util", "L0")

_emit_records_execution_trace("p0", "evidence", "list_layer_agents_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "list_layer_agents_util", "p0_governance")
_emit_snapshots_state("p0", "list_layer_agents_util", "state_snapshot")
_emit_authorize_and_execute("p2", "list_layer_agents_util", "execution_auth")
_emit_validates_capability("p2", "list_layer_agents_util", "capability_check")
_emit_routes_to_capability("p2", "list_layer_agents_util", "capability_route")
_emit_writes_via_uwg("p2", "list_layer_agents_util", "uwg_write")
_emit_blocks_direct_write("p2", "list_layer_agents_util", "direct_write_block")
_emit_records_tool_invocation("p2", "list_layer_agents_util", "tool_invocation")
_emit_captures_execution_output("p2", "list_layer_agents_util", "exec_output")
_emit_dispatches_agent("p3", "list_layer_agents_util", "agent_dispatch")
_emit_coordinates_agents("p3", "list_layer_agents_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "list_layer_agents_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "list_layer_agents_util", "healing_outcome")
_emit_escalates_failure("p3", "list_layer_agents_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "list_layer_agents_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "list_layer_agents_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "list_layer_agents_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "list_layer_agents_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "list_layer_agents_util", "eval_metric")
_emit_stores_embedding("p4", "list_layer_agents_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "list_layer_agents_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "list_layer_agents_util", "exec_snapshot_link")

layer = sys.argv[1] if len(sys.argv) > 1 else APPS_RG_DIR
data = json.load(open(AGENT_DISCOVERY_JSON))
agents = [a for a in data if a.get("layer") == layer]
print(f"{layer} agents ({len(agents)}):")
for a in agents:
    heal = "H" if a.get("has_healing") else "-"
    mcp = "M" if a.get("mcp_hardened") else "-"
    test = "T" if a.get("testing") != "None" else "-"
    print(f"  [{heal}{mcp}{test}] {a['class_name']} - {a['path']}")
