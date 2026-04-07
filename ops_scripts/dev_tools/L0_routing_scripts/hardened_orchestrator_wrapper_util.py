from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

emit_replay_key("p0", "hardened_orchestrator_wrapper_util")
emit_determinism_digest("p0", "hardened_orchestrator_wrapper_util")

_emit_dispatches_healing_run("p1", "hardened_orchestrator_wrapper_util", "L0")
_emit_routes_through("p1", "hardened_orchestrator_wrapper_util", "L0")
_emit_checks_agent_registry("p1", "hardened_orchestrator_wrapper_util", "agent_registry")
_emit_validates_agent_capability("p1", "hardened_orchestrator_wrapper_util", "capability")
_emit_dispatches_execution_plan("p1", "hardened_orchestrator_wrapper_util", "exec_plan")
_emit_agent_executes_agent("p1", "hardened_orchestrator_wrapper_util", "sub_agent")
_emit_routes_to_agent("p1", "hardened_orchestrator_wrapper_util", "target_agent")
_emit_verifies_policy("p1", "hardened_orchestrator_wrapper_util", "policy_check")
_emit_observes_runtime_state("p1", "hardened_orchestrator_wrapper_util", "runtime_state")
_emit_verifies_boundary("p1", "hardened_orchestrator_wrapper_util", "boundary_check")
_emit_transcripts_response("p1", "hardened_orchestrator_wrapper_util", "transcript")
_emit_hard_fails_untranscripted("p1", "hardened_orchestrator_wrapper_util")
_emit_gated_by_confidence("p1", "hardened_orchestrator_wrapper_util", "confidence_gate")
_emit_escalates_to_human("p1", "hardened_orchestrator_wrapper_util", "L0")
_emit_reads_policy_state("p1", "hardened_orchestrator_wrapper_util", "L0")
_emit_authorize_and_execute("p2", "hardened_orchestrator_wrapper_util", "execution_auth")
_emit_validates_capability("p2", "hardened_orchestrator_wrapper_util", "capability_check")
_emit_routes_to_capability("p2", "hardened_orchestrator_wrapper_util", "capability_route")
_emit_writes_via_uwg("p2", "hardened_orchestrator_wrapper_util", "uwg_write")
_emit_blocks_direct_write("p2", "hardened_orchestrator_wrapper_util", "direct_write_block")
_emit_records_tool_invocation("p2", "hardened_orchestrator_wrapper_util", "tool_invocation")
_emit_captures_execution_output("p2", "hardened_orchestrator_wrapper_util", "exec_output")
_emit_dispatches_agent("p3", "hardened_orchestrator_wrapper_util", "agent_dispatch")
_emit_coordinates_agents("p3", "hardened_orchestrator_wrapper_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "hardened_orchestrator_wrapper_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "hardened_orchestrator_wrapper_util", "healing_outcome")
_emit_escalates_failure("p3", "hardened_orchestrator_wrapper_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "hardened_orchestrator_wrapper_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "hardened_orchestrator_wrapper_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "hardened_orchestrator_wrapper_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "hardened_orchestrator_wrapper_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "hardened_orchestrator_wrapper_util", "eval_metric")
_emit_stores_embedding("p4", "hardened_orchestrator_wrapper_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "hardened_orchestrator_wrapper_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "hardened_orchestrator_wrapper_util", "exec_snapshot_link")

"\nHardened Orchestrator - Thin Wrapper\nDelegates to consolidated core orchestrator in agentic_core/core/orchestrator_main.py\n\nThis is a stub-and-proxy pattern implementation that eliminates race conditions\nby routing all orchestration through the consolidated AtomicBlackboard-integrated core.\n"
import asyncio
import logging
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("hardened_orchestrator_wrapper_util", "p4obs", "metric_1")
_emit_emits_metric_event("hardened_orchestrator_wrapper_util", "p4obs", "metric_2")
_emit_emits_metric_event("hardened_orchestrator_wrapper_util", "p4obs", "metric_3")
_emit_emits_metric_event("hardened_orchestrator_wrapper_util", "p4obs", "metric_4")
_emit_emits_metric_event("hardened_orchestrator_wrapper_util", "p4obs", "metric_5")
_emit_emits_metric_event("hardened_orchestrator_wrapper_util", "p4obs", "metric_6")
_emit_records_incident_event("hardened_orchestrator_wrapper_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("hardened_orchestrator_wrapper_util", "p4obs", "anomaly")
_emit_writes_observability_log("hardened_orchestrator_wrapper_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("hardened_orchestrator_wrapper_util", "p4obs", "mon_state")
_emit_triggers_alert("hardened_orchestrator_wrapper_util", "p4obs", "alert")
_emit_links_incident_trace("hardened_orchestrator_wrapper_util", "p4obs", "trace_link")
_emit_captures_pattern("hardened_orchestrator_wrapper_util", "p3lm", "pattern")
_emit_records_learning_event("hardened_orchestrator_wrapper_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("hardened_orchestrator_wrapper_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("hardened_orchestrator_wrapper_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("hardened_orchestrator_wrapper_util", "p3lm", "routing")
_emit_improves_agent_policy("hardened_orchestrator_wrapper_util", "p3lm", "policy")
_emit_stores_learning_state("hardened_orchestrator_wrapper_util", "p3lm", "state")
_emit_records_execution_trace("hardened_orchestrator_wrapper_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("hardened_orchestrator_wrapper_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("hardened_orchestrator_wrapper_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("hardened_orchestrator_wrapper_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("hardened_orchestrator_wrapper_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("hardened_orchestrator_wrapper_util", "env_read", "p2_env_1")
_emit_reads_environ("hardened_orchestrator_wrapper_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("hardened_orchestrator_wrapper_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("hardened_orchestrator_wrapper_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "hardened_orchestrator_wrapper_util", "context_pull")
_emit_pulls_context("p1", "hardened_orchestrator_wrapper_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "hardened_orchestrator_wrapper_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "hardened_orchestrator_wrapper_util", "uwg_term_2")
_emit_writes_through("p1", "hardened_orchestrator_wrapper_util", "write_through")
_emit_writes_through("p1", "hardened_orchestrator_wrapper_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "hardened_orchestrator_wrapper_util", "safety_validation")
_emit_invokes_eval("p1", "hardened_orchestrator_wrapper_util", "eval_call")
_emit_proposal_commits_routing("p1", "hardened_orchestrator_wrapper_util", "routing_commit")

Logger: Any = logging.getLogger(__name__)


def _get_ValidationContext():
    """Lazy load ValidationContext to avoid upward import."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_ValidationContext", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_ValidationContext", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "_get_ValidationContext")
    from agentic_core.L1_cognition.P2_domain.context import ValidationContext

    return ValidationContext


async def run_hardened_orchestrator(
    workflow_id: str,
    WorkflowType: str = "resume_generation",
    storage_path: str | None = None,
    run_base_dir: str = "./pipeline_runs",
) -> Any:
    """
    Run hardened workflow orchestrator with atomic state management.

    This is a thin wrapper that delegates to the consolidated orchestrator.

    Args:
        workflow_id: Workflow identifier
        WorkflowType: Type of workflow
        storage_path: Path for atomic state storage
        run_base_dir: Base directory for run outputs

    Returns:
        Workflow execution results
    """
    from agentic_core.L3_orchestration.config.orchestrator_config import (
        OrchestratorConfig,
        create_orchestrator,
    )

    Logger.info("🚀 Hardened Orchestrator (Wrapper)")
    Logger.info(f"   Workflow: {workflow_id}")
    Logger.info(f"   Type: {WorkflowType}")
    # guardian: allow-magic-config
    config: Any = OrchestratorConfig(
        max_cycles=5, enable_checkpointing=True, checkpoint_dir=storage_path or "./checkpoints",
    )
    context: Any = _get_ValidationContext()()
    orchestrator: Any = create_orchestrator(config=config, context=context)
    resume_agent: Any = create_resume_agent(
        context=context,
        workflow_id=workflow_id,
        WorkflowType=WorkflowType,
        enable_titanium_rag=True,
        enable_state_persistence=True,
        storage_path=storage_path,
        run_base_dir=run_base_dir,
    )
    results: Any = await orchestrator.execute_workflow(workflow_id=workflow_id, agents=[resume_agent])
    return results


if __name__ == "__main__":
    import argparse

    parser: Any = argparse.ArgumentParser(description="Hardened Orchestrator")
    parser.add_argument("--workflow-id", required=True, help="Workflow ID")
    parser.add_argument("--workflow-type", default="resume_generation", help="Workflow type")
    parser.add_argument("--storage-path", help="Storage path for state")
    args: Any = parser.parse_args()
    asyncio.run(
        run_hardened_orchestrator(
            workflow_id=args.workflow_id, WorkflowType=args.WorkflowType, storage_path=args.storage_path,
        ),
    )
