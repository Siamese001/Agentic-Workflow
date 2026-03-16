"""Generate simple layer summary table."""

import json
from collections import defaultdict

from agentic_core.L0_routing.config import AGENT_DISCOVERY_JSON, TESTS_DIR
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

emit_replay_key("p0", "layer_summary_util")
emit_determinism_digest("p0", "layer_summary_util")

_emit_dispatches_healing_run("p1", "layer_summary_util", "L0")
_emit_routes_through("p1", "layer_summary_util", "L0")
_emit_escalates_to_human("p1", "layer_summary_util", "L0")
_emit_reads_policy_state("p1", "layer_summary_util", "L0")

_emit_records_execution_trace("p0", "evidence", "layer_summary_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "layer_summary_util", "p0_governance")
_emit_snapshots_state("p0", "layer_summary_util", "state_snapshot")
_emit_authorize_and_execute("p2", "layer_summary_util", "execution_auth")
_emit_validates_capability("p2", "layer_summary_util", "capability_check")
_emit_routes_to_capability("p2", "layer_summary_util", "capability_route")
_emit_writes_via_uwg("p2", "layer_summary_util", "uwg_write")
_emit_blocks_direct_write("p2", "layer_summary_util", "direct_write_block")
_emit_records_tool_invocation("p2", "layer_summary_util", "tool_invocation")
_emit_captures_execution_output("p2", "layer_summary_util", "exec_output")
_emit_dispatches_agent("p3", "layer_summary_util", "agent_dispatch")
_emit_coordinates_agents("p3", "layer_summary_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "layer_summary_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "layer_summary_util", "healing_outcome")
_emit_escalates_failure("p3", "layer_summary_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "layer_summary_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "layer_summary_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "layer_summary_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "layer_summary_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "layer_summary_util", "eval_metric")
_emit_stores_embedding("p4", "layer_summary_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "layer_summary_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "layer_summary_util", "exec_snapshot_link")

data = json.load(open(AGENT_DISCOVERY_JSON))
stats = defaultdict(lambda: {"count": 0, "healing": 0, "mcp": 0, "testing": 0, "tools": 0})
for a in data:
    layer = a.get("layer", "misc")
    stats[layer]["count"] += 1
    if a.get("has_healing"):
        stats[layer]["healing"] += 1
    if a.get("mcp_hardened"):
        stats[layer]["mcp"] += 1
    if a.get("testing") != "None":
        stats[layer]["testing"] += 1
    if a.get("has_tools"):
        stats[layer]["tools"] += 1
print("| Layer | Agents | Healing | MCP Hardened | Testing | Tools |")
print("|-------|--------|---------|--------------|---------|-------|")
for layer in [
    "L0",
    "L1",
    "L2",
    "L3",
    "L4",
    "L5",
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    TESTS_DIR,
    "misc",
]:
    s = stats[layer]
    if s["count"] > 0:
        h_pct = 100 * s["healing"] // s["count"]
        m_pct = 100 * s["mcp"] // s["count"]
        t_pct = 100 * s["testing"] // s["count"]
        tl_pct = 100 * s["tools"] // s["count"]
        print(
            f"| {layer} | {s['count']} | {s['healing']} ({h_pct}%) | {s['mcp']} ({m_pct}%) | {s['testing']} ({t_pct}%) | {s['tools']} ({tl_pct}%) |"
        )
total = sum(s["count"] for s in stats.values())
heal = sum(s["healing"] for s in stats.values())
mcp = sum(s["mcp"] for s in stats.values())
test = sum(s["testing"] for s in stats.values())
tools = sum(s["tools"] for s in stats.values())
print(
    f"| **TOTAL** | **{total}** | **{heal}** ({100 * heal // total}%) | **{mcp}** ({100 * mcp // total}%) | **{test}** ({100 * test // total}%) | **{tools}** ({100 * tools // total}%) |"
)
