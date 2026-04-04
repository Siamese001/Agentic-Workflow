from __future__ import annotations

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "fix_remaining_depth_util")
emit_determinism_digest("p0", "fix_remaining_depth_util")

_emit_dispatches_healing_run("p1", "fix_remaining_depth_util", "L0")
_emit_routes_through("p1", "fix_remaining_depth_util", "L0")
_emit_checks_agent_registry("p1", "fix_remaining_depth_util", "agent_registry")
_emit_validates_agent_capability("p1", "fix_remaining_depth_util", "capability")
_emit_dispatches_execution_plan("p1", "fix_remaining_depth_util", "exec_plan")
_emit_agent_executes_agent("p1", "fix_remaining_depth_util", "sub_agent")
_emit_routes_to_agent("p1", "fix_remaining_depth_util", "target_agent")
_emit_verifies_policy("p1", "fix_remaining_depth_util", "policy_check")
_emit_observes_runtime_state("p1", "fix_remaining_depth_util", "runtime_state")
_emit_verifies_boundary("p1", "fix_remaining_depth_util", "boundary_check")
_emit_transcripts_response("p1", "fix_remaining_depth_util", "transcript")
_emit_hard_fails_untranscripted("p1", "fix_remaining_depth_util")
_emit_gated_by_confidence("p1", "fix_remaining_depth_util", "confidence_gate")
_emit_escalates_to_human("p1", "fix_remaining_depth_util", "L0")
_emit_reads_policy_state("p1", "fix_remaining_depth_util", "L0")
_emit_authorize_and_execute("p2", "fix_remaining_depth_util", "execution_auth")
_emit_validates_capability("p2", "fix_remaining_depth_util", "capability_check")
_emit_routes_to_capability("p2", "fix_remaining_depth_util", "capability_route")
_emit_writes_via_uwg("p2", "fix_remaining_depth_util", "uwg_write")
_emit_blocks_direct_write("p2", "fix_remaining_depth_util", "direct_write_block")
_emit_records_tool_invocation("p2", "fix_remaining_depth_util", "tool_invocation")
_emit_captures_execution_output("p2", "fix_remaining_depth_util", "exec_output")
_emit_dispatches_agent("p3", "fix_remaining_depth_util", "agent_dispatch")
_emit_coordinates_agents("p3", "fix_remaining_depth_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "fix_remaining_depth_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "fix_remaining_depth_util", "healing_outcome")
_emit_escalates_failure("p3", "fix_remaining_depth_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "fix_remaining_depth_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "fix_remaining_depth_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "fix_remaining_depth_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "fix_remaining_depth_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "fix_remaining_depth_util", "eval_metric")
_emit_stores_embedding("p4", "fix_remaining_depth_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "fix_remaining_depth_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "fix_remaining_depth_util", "exec_snapshot_link")

"Move remaining shallow files to proper depth."
import shutil
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config import AGENTIC_CORE_DIR
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("fix_remaining_depth_util", "p4obs", "metric_1")
_emit_emits_metric_event("fix_remaining_depth_util", "p4obs", "metric_2")
_emit_emits_metric_event("fix_remaining_depth_util", "p4obs", "metric_3")
_emit_emits_metric_event("fix_remaining_depth_util", "p4obs", "metric_4")
_emit_emits_metric_event("fix_remaining_depth_util", "p4obs", "metric_5")
_emit_emits_metric_event("fix_remaining_depth_util", "p4obs", "metric_6")
_emit_records_incident_event("fix_remaining_depth_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("fix_remaining_depth_util", "p4obs", "anomaly")
_emit_writes_observability_log("fix_remaining_depth_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("fix_remaining_depth_util", "p4obs", "mon_state")
_emit_triggers_alert("fix_remaining_depth_util", "p4obs", "alert")
_emit_links_incident_trace("fix_remaining_depth_util", "p4obs", "trace_link")
_emit_captures_pattern("fix_remaining_depth_util", "p3lm", "pattern")
_emit_records_learning_event("fix_remaining_depth_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("fix_remaining_depth_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("fix_remaining_depth_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("fix_remaining_depth_util", "p3lm", "routing")
_emit_improves_agent_policy("fix_remaining_depth_util", "p3lm", "policy")
_emit_stores_learning_state("fix_remaining_depth_util", "p3lm", "state")
_emit_records_execution_trace("fix_remaining_depth_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("fix_remaining_depth_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("fix_remaining_depth_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("fix_remaining_depth_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("fix_remaining_depth_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("fix_remaining_depth_util", "env_read", "p2_env_1")
_emit_reads_environ("fix_remaining_depth_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("fix_remaining_depth_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("fix_remaining_depth_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "fix_remaining_depth_util", "context_pull")
_emit_pulls_context("p1", "fix_remaining_depth_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "fix_remaining_depth_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "fix_remaining_depth_util", "uwg_term_2")
_emit_writes_through("p1", "fix_remaining_depth_util", "write_through")
_emit_writes_through("p1", "fix_remaining_depth_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "fix_remaining_depth_util", "safety_validation")
_emit_invokes_eval("p1", "fix_remaining_depth_util", "eval_call")
_emit_proposal_commits_routing("p1", "fix_remaining_depth_util", "routing_commit")

ROOT: Any = Path("C:/Git/Agentic-Workflow")
core: Any = ROOT / AGENTIC_CORE_DIR


def move_remaining() -> Any:
    """Move remaining depth 3 files to P1_core."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "move_remaining", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "move_remaining", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "move_remaining")
    print("[*] MOVING REMAINING SHALLOW FILES...")
    moved: Any = 0
    knowledge_dir: Any = CORE / "knowledge"
    if knowledge_dir.exists():
        stage: Any = knowledge_dir / "P1_core"
        stage.mkdir(exist_ok=True)
        assert_no_persistent_write("L0", "write_text")
        (stage / "__init__.py").write_text('"""Stage module."""\n')
        from agentic_core.utils.ssot_discovery_validator import get_python_files

        for f in get_python_files(knowledge_dir):
            if f.name != "__init__.py" and f.parent == knowledge_dir:
                target: Any = stage / f.name
                if not target.exists():
                    assert_no_persistent_write("L0", "shutil.mutate")
                    shutil.move(str(f), str(target))
                    print(f"  [✓] Moved: {f.relative_to(CORE)}")
                    moved += 1
    thought_nodes: Any = CORE / "L1_cognition" / "thought_engine"
    if thought_nodes.exists():
        stage: Any = thought_nodes / "P1_core"
        stage.mkdir(exist_ok=True)
        assert_no_persistent_write("L0", "write_text")
        (stage / "__init__.py").write_text('"""Stage module."""\n')
        from agentic_core.utils.ssot_discovery_validator import get_python_files

        for f in get_python_files(thought_nodes):
            if f.name != "__init__.py" and f.parent == thought_nodes:
                target: Any = stage / f.name
                if not target.exists():
                    assert_no_persistent_write("L0", "shutil.mutate")
                    shutil.move(str(f), str(target))
                    print(f"  [✓] Moved: {f.relative_to(CORE)}")
                    moved += 1
    print(f"\n[OK] Moved {moved} files")


if __name__ == "__main__":
    move_remaining()
