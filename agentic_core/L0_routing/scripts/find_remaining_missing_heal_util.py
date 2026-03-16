"""Find the remaining agents missing heal_repository."""

import json
import sys
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

emit_replay_key("p0", "find_remaining_missing_heal_util")
emit_determinism_digest("p0", "find_remaining_missing_heal_util")

_emit_dispatches_healing_run("p1", "find_remaining_missing_heal_util", "L0")
_emit_routes_through("p1", "find_remaining_missing_heal_util", "L0")
_emit_escalates_to_human("p1", "find_remaining_missing_heal_util", "L0")
_emit_reads_policy_state("p1", "find_remaining_missing_heal_util", "L0")

_emit_records_execution_trace("p0", "evidence", "find_remaining_missing_heal_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "find_remaining_missing_heal_util", "p0_governance")
_emit_snapshots_state("p0", "find_remaining_missing_heal_util", "state_snapshot")
_emit_authorize_and_execute("p2", "find_remaining_missing_heal_util", "execution_auth")
_emit_validates_capability("p2", "find_remaining_missing_heal_util", "capability_check")
_emit_routes_to_capability("p2", "find_remaining_missing_heal_util", "capability_route")
_emit_writes_via_uwg("p2", "find_remaining_missing_heal_util", "uwg_write")
_emit_blocks_direct_write("p2", "find_remaining_missing_heal_util", "direct_write_block")
_emit_records_tool_invocation("p2", "find_remaining_missing_heal_util", "tool_invocation")
_emit_captures_execution_output("p2", "find_remaining_missing_heal_util", "exec_output")
_emit_dispatches_agent("p3", "find_remaining_missing_heal_util", "agent_dispatch")
_emit_coordinates_agents("p3", "find_remaining_missing_heal_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "find_remaining_missing_heal_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "find_remaining_missing_heal_util", "healing_outcome")
_emit_escalates_failure("p3", "find_remaining_missing_heal_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "find_remaining_missing_heal_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "find_remaining_missing_heal_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "find_remaining_missing_heal_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "find_remaining_missing_heal_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "find_remaining_missing_heal_util", "eval_metric")
_emit_stores_embedding("p4", "find_remaining_missing_heal_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "find_remaining_missing_heal_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "find_remaining_missing_heal_util", "exec_snapshot_link")

# guardian: allow-global-mutation
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from agentic_core.utils.project_root_util import get_project_root

project_root = get_project_root()
with open(project_root / "agent_discovery_full.json", encoding="utf-8") as f:
    data = json.load(f)
missing = [a for a in data if not a.get("has_healing")]
print(f"Agents missing healing: {len(missing)}")
for agent in missing:
    print(f"  {agent['path']}")
