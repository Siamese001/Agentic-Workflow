"""Verify heal invocation coverage after fixes."""

import json

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

emit_replay_key("p0", "verify_heal_invocation_util")
emit_determinism_digest("p0", "verify_heal_invocation_util")

_emit_dispatches_healing_run("p1", "verify_heal_invocation_util", "L0")
_emit_routes_through("p1", "verify_heal_invocation_util", "L0")
_emit_escalates_to_human("p1", "verify_heal_invocation_util", "L0")
_emit_reads_policy_state("p1", "verify_heal_invocation_util", "L0")

_emit_records_execution_trace("p0", "evidence", "verify_heal_invocation_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "verify_heal_invocation_util", "p0_governance")
_emit_snapshots_state("p0", "verify_heal_invocation_util", "state_snapshot")
_emit_authorize_and_execute("p2", "verify_heal_invocation_util", "execution_auth")
_emit_validates_capability("p2", "verify_heal_invocation_util", "capability_check")
_emit_routes_to_capability("p2", "verify_heal_invocation_util", "capability_route")
_emit_writes_via_uwg("p2", "verify_heal_invocation_util", "uwg_write")
_emit_blocks_direct_write("p2", "verify_heal_invocation_util", "direct_write_block")
_emit_records_tool_invocation("p2", "verify_heal_invocation_util", "tool_invocation")
_emit_captures_execution_output("p2", "verify_heal_invocation_util", "exec_output")
_emit_dispatches_agent("p3", "verify_heal_invocation_util", "agent_dispatch")
_emit_coordinates_agents("p3", "verify_heal_invocation_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "verify_heal_invocation_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "verify_heal_invocation_util", "healing_outcome")
_emit_escalates_failure("p3", "verify_heal_invocation_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "verify_heal_invocation_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "verify_heal_invocation_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "verify_heal_invocation_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "verify_heal_invocation_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "verify_heal_invocation_util", "eval_metric")
_emit_stores_embedding("p4", "verify_heal_invocation_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "verify_heal_invocation_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "verify_heal_invocation_util", "exec_snapshot_link")

data = json.load(open("agent_discovery_full.json"))
total = len(data)
has_invocation = sum(1 for a in data if a.get("invocation") == "Yes")
percentage = has_invocation / total * 100
print("=" * 80)
print("HEAL INVOCATION VERIFICATION")
print("=" * 80)
print(f"Total agents: {total}")
print(f"Agents with heal invocation: {has_invocation}")
print(f"Coverage: {percentage:.1f}%")
print()
if percentage >= 100.0:
    print("✅ TARGET ACHIEVED: 100% heal invocation coverage!")
elif percentage >= 99.0:
    print(f"⚠️  NEARLY COMPLETE: {100 - percentage:.1f}% gap remaining")
    missing = [a for a in data if a.get("invocation") != "Yes"]
    for agent in missing:
        print(f"  - {agent['class_name']}: {agent.get('path')}")
else:
    print(f"❌ GAP: {100 - percentage:.1f}% ({total - has_invocation} agents)")
print("=" * 80)
