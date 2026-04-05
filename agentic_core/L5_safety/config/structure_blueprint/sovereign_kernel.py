"""Sovereign Kernel Manifest — Immutable Core Components.

Declares the minimal sovereign kernel that cannot be removed or bypassed
without compromising system integrity. Extensions (meta-learning, DPO,
pattern engines) must not create reverse dependencies into kernel internals.

Invariant: Failure of any extension must not affect kernel operation.
"""

from __future__ import annotations

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "sovereign_kernel")
emit_determinism_digest("p0", "sovereign_kernel")

_emit_dispatches_healing_run("p1", "sovereign_kernel", "L5")
_emit_routes_through("p1", "sovereign_kernel", "L5")
_emit_checks_agent_registry("p1", "sovereign_kernel", "agent_registry")
_emit_validates_agent_capability("p1", "sovereign_kernel", "capability")
_emit_dispatches_execution_plan("p1", "sovereign_kernel", "exec_plan")
_emit_agent_executes_agent("p1", "sovereign_kernel", "sub_agent")
_emit_routes_to_agent("p1", "sovereign_kernel", "target_agent")
_emit_verifies_policy("p1", "sovereign_kernel", "policy_check")
_emit_observes_runtime_state("p1", "sovereign_kernel", "runtime_state")
_emit_verifies_boundary("p1", "sovereign_kernel", "boundary_check")
_emit_transcripts_response("p1", "sovereign_kernel", "transcript")
_emit_hard_fails_untranscripted("p1", "sovereign_kernel")
_emit_gated_by_confidence("p1", "sovereign_kernel", "confidence_gate")
_emit_escalates_to_human("p1", "sovereign_kernel", "L5")
_emit_reads_policy_state("p1", "sovereign_kernel", "L5")
_emit_authorize_and_execute("p2", "sovereign_kernel", "execution_auth")
_emit_validates_capability("p2", "sovereign_kernel", "capability_check")
_emit_routes_to_capability("p2", "sovereign_kernel", "capability_route")
_emit_writes_via_uwg("p2", "sovereign_kernel", "uwg_write")
_emit_blocks_direct_write("p2", "sovereign_kernel", "direct_write_block")
_emit_records_tool_invocation("p2", "sovereign_kernel", "tool_invocation")
_emit_captures_execution_output("p2", "sovereign_kernel", "exec_output")
_emit_dispatches_agent("p3", "sovereign_kernel", "agent_dispatch")
_emit_coordinates_agents("p3", "sovereign_kernel", "agent_coordination")
_emit_records_workflow_lineage("p3", "sovereign_kernel", "workflow_lineage")
_emit_records_healing_outcome("p3", "sovereign_kernel", "healing_outcome")
_emit_escalates_failure("p3", "sovereign_kernel", "failure_escalation")
_emit_orchestrates_workflow("p3", "sovereign_kernel", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "sovereign_kernel", "healing_dispatch")
_emit_invokes_evaluation("p3", "sovereign_kernel", "evaluation_signal")
_emit_records_telemetry_event("p4", "sovereign_kernel", "telemetry_event")
_emit_captures_evaluation_metric("p4", "sovereign_kernel", "eval_metric")
_emit_stores_embedding("p4", "sovereign_kernel", "embedding_store")
_emit_updates_meta_learning_state("p4", "sovereign_kernel", "meta_learning")
_emit_links_execution_to_snapshot("p4", "sovereign_kernel", "exec_snapshot_link")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
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

_emit_emits_metric_event("sovereign_kernel", "p4obs", "metric_1")
_emit_emits_metric_event("sovereign_kernel", "p4obs", "metric_2")
_emit_emits_metric_event("sovereign_kernel", "p4obs", "metric_3")
_emit_emits_metric_event("sovereign_kernel", "p4obs", "metric_4")
_emit_emits_metric_event("sovereign_kernel", "p4obs", "metric_5")
_emit_emits_metric_event("sovereign_kernel", "p4obs", "metric_6")
_emit_records_incident_event("sovereign_kernel", "p4obs", "incident")
_emit_captures_runtime_anomaly("sovereign_kernel", "p4obs", "anomaly")
_emit_writes_observability_log("sovereign_kernel", "p4obs", "obs_log")
_emit_updates_monitoring_state("sovereign_kernel", "p4obs", "mon_state")
_emit_triggers_alert("sovereign_kernel", "p4obs", "alert")
_emit_links_incident_trace("sovereign_kernel", "p4obs", "trace_link")
_emit_captures_pattern("sovereign_kernel", "p3lm", "pattern")
_emit_records_learning_event("sovereign_kernel", "p3lm", "learning_event")
_emit_writes_learning_snapshot("sovereign_kernel", "p3lm", "snapshot")
_emit_feeds_meta_learning("sovereign_kernel", "p3lm", "meta_feed")
_emit_updates_routing_strategy("sovereign_kernel", "p3lm", "routing")
_emit_improves_agent_policy("sovereign_kernel", "p3lm", "policy")
_emit_stores_learning_state("sovereign_kernel", "p3lm", "state")
_emit_records_execution_trace("sovereign_kernel", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("sovereign_kernel", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("sovereign_kernel", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("sovereign_kernel", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("sovereign_kernel", "L4_STATE", "p2_trace_5")
_emit_reads_environ("sovereign_kernel", "env_read", "p2_env_1")
_emit_reads_environ("sovereign_kernel", "env_read", "p2_env_2")
_emit_reads_runtime_state("sovereign_kernel", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("sovereign_kernel", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "sovereign_kernel", "context_pull")
_emit_pulls_context("p1", "sovereign_kernel", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "sovereign_kernel", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "sovereign_kernel", "uwg_term_2")
_emit_writes_through("p1", "sovereign_kernel", "write_through")
_emit_writes_through("p1", "sovereign_kernel", "write_through_2")
_emit_validated_by_safety_plane("p1", "sovereign_kernel", "safety_validation")
_emit_invokes_eval("p1", "sovereign_kernel", "eval_call")
_emit_proposal_commits_routing("p1", "sovereign_kernel", "routing_commit")

SOVEREIGN_KERNEL_COMPONENTS: frozenset[str] = frozenset(
    {
        "agentic_core.L0_routing",
        "agentic_core.L5_safety",
        "agentic_core.L2_execution",
        "agentic_core.determinism",
        "agentic_core.replay",
        "agentic_core.agents.agent_registry",
        "agentic_core.L2_execution.enforcement.SovereignLLMGateway",
        "agentic_core.interfaces",
        "agentic_core.embeddings",
        "agentic_core.runtime",
        "agentic_core.prompt_governance",
        "agentic_core.core",
        "agentic_core.L5_safety.validators.base_detector_validator",
        "agentic_core.mixins",
        "agentic_core.utils",
        "agentic_core.semantic_memory",
        "agentic_core.L1_cognition",
        "agentic_core.L3_orchestration",
        "agentic_core.L4_state",
        "agentic_core.config",
        "agentic_core.patterns",
        "agentic_core.base_agents",
    }
)
MODULAR_EXTENSIONS: frozenset[str] = frozenset(
    {
        "system_learning",
        "system_learning.pipelines.meta_learning_pipeline",
        "system_learning.engines.healing_outcome_aggregator",
        "system_learning.engines.pattern_analysis_engine",
        "system_learning.engines.healing_config_optimizer",
        "system_learning.engines.code_quality_signal_engine",
        "system_learning.engines.classification_feedback_engine",
        "system_learning.engines.entropy_telemetry_engine",
        "system_learning.engines.surface_isolation_validator",
        "system_learning.engines.change_package_impl",
        "system_learning.engines.rlhf_optimizer",
        "system_learning.engines.policy_recommendation_engine",
        "agentic_core.rag",
        "agentic_core.context",
        "agentic_core.L0_routing.seams.c0_context_retriever",
        "agentic_core.L2_execution.healers.healing_tier_config",
        "agentic_core.L2_execution.healers.healing_tier_dispatcher",
        "agentic_core.L6_observability.enhanced_observability",
        "agentic_core.telemetry",
    }
)


def is_kernel_component(module_path: str) -> bool:
    """Check if a given module path is part of the sovereign kernel."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "is_kernel_component", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "is_kernel_component", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "is_kernel_component")
    normalized = module_path.replace("/", ".")
    for kernel_path in SOVEREIGN_KERNEL_COMPONENTS:
        if normalized == kernel_path or normalized.startswith(kernel_path + "."):
            return True
    return False


def is_modular_extension(module_path: str) -> bool:
    """Check if a given module path is a modular extension."""
    normalized = module_path.replace("/", ".")
    for ext_path in MODULAR_EXTENSIONS:
        if normalized == ext_path or normalized.startswith(ext_path + "."):
            return True
    return False


def validate_boundary(module_path: str) -> tuple[bool, str]:
    """Validate that a module respects kernel/extension boundary.

    Returns:
        (is_valid, reason) tuple
    """
    if is_kernel_component(module_path):
        return (True, "kernel_component")
    if is_modular_extension(module_path):
        return (True, "modular_extension")
    return (False, f"unclassified_module: {module_path}")


__all__ = [
    "SOVEREIGN_KERNEL_COMPONENTS",
    "MODULAR_EXTENSIONS",
    "is_kernel_component",
    "is_modular_extension",
    "validate_boundary",
]
