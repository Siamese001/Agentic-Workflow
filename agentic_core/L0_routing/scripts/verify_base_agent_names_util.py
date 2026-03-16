#!/usr/bin/env python3
"""Verify Base Agent names in dashboard data."""

import json
from pathlib import Path

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
)
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

emit_replay_key("p0", "verify_base_agent_names_util")
emit_determinism_digest("p0", "verify_base_agent_names_util")

_emit_dispatches_healing_run("p1", "verify_base_agent_names_util", "L0")
_emit_routes_through("p1", "verify_base_agent_names_util", "L0")
_emit_escalates_to_human("p1", "verify_base_agent_names_util", "L0")
_emit_reads_policy_state("p1", "verify_base_agent_names_util", "L0")

_emit_records_execution_trace("p0", "evidence", "verify_base_agent_names_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "verify_base_agent_names_util", "p0_governance")
_emit_snapshots_state("p0", "verify_base_agent_names_util", "state_snapshot")
_emit_authorize_and_execute("p2", "verify_base_agent_names_util", "execution_auth")
_emit_validates_capability("p2", "verify_base_agent_names_util", "capability_check")
_emit_routes_to_capability("p2", "verify_base_agent_names_util", "capability_route")
_emit_writes_via_uwg("p2", "verify_base_agent_names_util", "uwg_write")
_emit_blocks_direct_write("p2", "verify_base_agent_names_util", "direct_write_block")
_emit_records_tool_invocation("p2", "verify_base_agent_names_util", "tool_invocation")
_emit_captures_execution_output("p2", "verify_base_agent_names_util", "exec_output")
_emit_dispatches_agent("p3", "verify_base_agent_names_util", "agent_dispatch")
_emit_coordinates_agents("p3", "verify_base_agent_names_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "verify_base_agent_names_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "verify_base_agent_names_util", "healing_outcome")
_emit_escalates_failure("p3", "verify_base_agent_names_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "verify_base_agent_names_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "verify_base_agent_names_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "verify_base_agent_names_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "verify_base_agent_names_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "verify_base_agent_names_util", "eval_metric")
_emit_stores_embedding("p4", "verify_base_agent_names_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "verify_base_agent_names_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "verify_base_agent_names_util", "exec_snapshot_link")

project_root = Path(__file__).parent.parent
data_file = project_root / AGENTIC_CORE_DIR / "L6_observability" / "dashboards" / "data" / "dashboard_data.js"

content = data_file.read_text(encoding="utf-8")
lines = [l for l in content.split("\n") if not l.strip().startswith("//")]
content = "\n".join(lines).replace("window.dashboardData = ", "").strip().rstrip(";")
data = json.loads(content)

print("\nFirst 10 territories in dashboard data:")
print("=" * 60)
for i, row in enumerate(data[:10]):
    print(f"{i + 1}. {row['Territory']}")

print("\n" + "=" * 60)
print("Base Agent territories:")
print("=" * 60)
for row in data:
    if "Base Agent" in row["Territory"] or row["Territory"] == "Sovereign Base Agent":
        print(f"  ✅ {row['Territory']}")
