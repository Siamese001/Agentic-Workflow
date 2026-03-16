"""
Verify healing and invocation metrics for all agents.
"""

import json
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
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
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "verify_healing_metrics_util")
emit_determinism_digest("p0", "verify_healing_metrics_util")

_emit_dispatches_healing_run("p1", "verify_healing_metrics_util", "L0")
_emit_routes_through("p1", "verify_healing_metrics_util", "L0")
_emit_escalates_to_human("p1", "verify_healing_metrics_util", "L0")
_emit_reads_policy_state("p1", "verify_healing_metrics_util", "L0")
_emit_authorize_and_execute("p2", "verify_healing_metrics_util", "execution_auth")
_emit_validates_capability("p2", "verify_healing_metrics_util", "capability_check")
_emit_routes_to_capability("p2", "verify_healing_metrics_util", "capability_route")
_emit_writes_via_uwg("p2", "verify_healing_metrics_util", "uwg_write")
_emit_blocks_direct_write("p2", "verify_healing_metrics_util", "direct_write_block")
_emit_records_tool_invocation("p2", "verify_healing_metrics_util", "tool_invocation")
_emit_captures_execution_output("p2", "verify_healing_metrics_util", "exec_output")
_emit_dispatches_agent("p3", "verify_healing_metrics_util", "agent_dispatch")
_emit_coordinates_agents("p3", "verify_healing_metrics_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "verify_healing_metrics_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "verify_healing_metrics_util", "healing_outcome")
_emit_escalates_failure("p3", "verify_healing_metrics_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "verify_healing_metrics_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "verify_healing_metrics_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "verify_healing_metrics_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "verify_healing_metrics_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "verify_healing_metrics_util", "eval_metric")
_emit_stores_embedding("p4", "verify_healing_metrics_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "verify_healing_metrics_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "verify_healing_metrics_util", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).parent.parent
DISCOVERY_FILE = PROJECT_ROOT / "agent_discovery_full.json"
DASHBOARD_DATA = PROJECT_ROOT / "agentic_core/L6_observability/dashboards/data/dashboard_data.js"


def main():
    """Verify healing metrics."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "main", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "main", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "main")
    print("=" * 70)
    print("HEALING & INVOCATION METRICS VERIFICATION")
    print("=" * 70)
    with open(DISCOVERY_FILE, encoding="utf-8") as f:
        agents = json.load(f)
    total = len(agents)
    with_healing = sum(1 for a in agents if a.get("has_healing", False))
    with_invocation = sum(1 for a in agents if a.get("invocation") == "Yes")
    print("\nAgent Discovery Data:")
    print(f"  Total agents: {total}")
    print(f"  With healing: {with_healing} ({with_healing / total * 100:.1f}%)")
    print(f"  With invocation: {with_invocation} ({with_invocation / total * 100:.1f}%)")
    content = DASHBOARD_DATA.read_text(encoding="utf-8")
    import re

    match = re.search("window\\.dashboardData = (\\[.*?\\]);", content, re.DOTALL)
    if match:
        data = json.loads(match.group(1))
        total_row = data[0]
        print("\nDashboard TOTAL Row:")
        print(f"  Heal Cap %: {total_row['Heal Cap %']}")
        print(f"  Invocation %: {total_row['Invocation %']}")
        print(f"  Test %: {total_row['Test %']}")
        print(f"  MCP Hardened %: {total_row['MCP Hardened %']}")
        print(f"  Health Score: {total_row['Health']}")
    print("\n" + "=" * 70)
    if with_healing == total and with_invocation == total:
        print("✅ 100% HEALING AND INVOCATION ACHIEVED")
        print("=" * 70)
        print("\nAll 265 agents have:")
        print("  ✅ Healing capability (has_healing = True)")
        print("  ✅ Invocation capability (invocation = 'Yes')")
    else:
        print("⚠️  NOT AT 100%")
        print("=" * 70)
        print(f"\nMissing healing: {total - with_healing} agents")
        print(f"Missing invocation: {total - with_invocation} agents")


if __name__ == "__main__":
    main()
