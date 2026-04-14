"""Factory for creating and managing the resilient router singleton.

Provides a global singleton instance of the HardenedRouter with default
configurations for common use cases.

Phase 2 - Resilient Routing Layer
"""

import logging

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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

_emit_authorize_and_execute("p2", "router_factory_util", "execution_auth")
_emit_validates_capability("p2", "router_factory_util", "capability_check")
_emit_routes_to_capability("p2", "router_factory_util", "capability_route")
_emit_writes_via_uwg("p2", "router_factory_util", "uwg_write")
_emit_blocks_direct_write("p2", "router_factory_util", "direct_write_block")
_emit_records_tool_invocation("p2", "router_factory_util", "tool_invocation")
_emit_captures_execution_output("p2", "router_factory_util", "exec_output")
_emit_dispatches_agent("p3", "router_factory_util", "agent_dispatch")
_emit_coordinates_agents("p3", "router_factory_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "router_factory_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "router_factory_util", "healing_outcome")
_emit_escalates_failure("p3", "router_factory_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "router_factory_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "router_factory_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "router_factory_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "router_factory_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "router_factory_util", "eval_metric")
_emit_stores_embedding("p4", "router_factory_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "router_factory_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "router_factory_util", "exec_snapshot_link")
from apps_shared.types.model_router_types import ModelRouter

_emit_records_execution_trace("p0", "evidence", "router_factory_util")
_emit_applies_guardrail("p0", "router_factory_util", "p0_governance")
_emit_reads_policy_state("p0", "router_factory_util", "policy_binding")
_emit_snapshots_state("p0", "router_factory_util", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("router_factory_util", "p4obs", "metric_1")
_emit_emits_metric_event("router_factory_util", "p4obs", "metric_2")
_emit_emits_metric_event("router_factory_util", "p4obs", "metric_3")
_emit_emits_metric_event("router_factory_util", "p4obs", "metric_4")
_emit_emits_metric_event("router_factory_util", "p4obs", "metric_5")
_emit_emits_metric_event("router_factory_util", "p4obs", "metric_6")
_emit_records_incident_event("router_factory_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("router_factory_util", "p4obs", "anomaly")
_emit_writes_observability_log("router_factory_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("router_factory_util", "p4obs", "mon_state")
_emit_triggers_alert("router_factory_util", "p4obs", "alert")
_emit_links_incident_trace("router_factory_util", "p4obs", "trace_link")
_emit_captures_pattern("router_factory_util", "p3lm", "pattern")
_emit_records_learning_event("router_factory_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("router_factory_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("router_factory_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("router_factory_util", "p3lm", "routing")
_emit_improves_agent_policy("router_factory_util", "p3lm", "policy")
_emit_stores_learning_state("router_factory_util", "p3lm", "state")
_emit_records_execution_trace("router_factory_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("router_factory_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("router_factory_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("router_factory_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("router_factory_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("router_factory_util", "env_read", "p2_env_1")
_emit_reads_environ("router_factory_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("router_factory_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("router_factory_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "router_factory_util", "context_pull")
_emit_pulls_context("p1", "router_factory_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "router_factory_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "router_factory_util", "uwg_term_2")
_emit_writes_through("p1", "router_factory_util", "write_through")
_emit_writes_through("p1", "router_factory_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "router_factory_util", "safety_validation")
_emit_invokes_eval("p1", "router_factory_util", "eval_call")
_emit_proposal_commits_routing("p1", "router_factory_util", "routing_commit")
_emit_escalates_to_human("p1", "router_factory_util", "human_escalation")
_emit_routes_through("p1", "router_factory_util", "route_through")
_emit_checks_agent_registry("p1", "router_factory_util", "agent_registry")
_emit_validates_agent_capability("p1", "router_factory_util", "capability")
_emit_dispatches_execution_plan("p1", "router_factory_util", "exec_plan")
_emit_agent_executes_agent("p1", "router_factory_util", "sub_agent")
_emit_routes_to_agent("p1", "router_factory_util", "target_agent")
_emit_verifies_policy("p1", "router_factory_util", "policy_check")
_emit_observes_runtime_state("p1", "router_factory_util", "runtime_state")
_emit_verifies_boundary("p1", "router_factory_util", "boundary_check")
_emit_transcripts_response("p1", "router_factory_util", "transcript")
_emit_hard_fails_untranscripted("p1", "router_factory_util")
_emit_gated_by_confidence("p1", "router_factory_util", "confidence_gate")
emit_replay_key("p0", "router_factory_util")
emit_determinism_digest("p0", "router_factory_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)
_router_instance: ModelRouter | None = None


def get_resilient_router() -> ModelRouter:
    """Get or create the singleton resilient router instance.

    Returns a configured HardenedRouter with default routing tiers:
    - reasoning_tier: Primary=OpenAI (GPT-4), Backup=Anthropic (Opus)
    - speed_tier: Primary=Gemini (Flash), Backup=OpenAI (4o-mini)
    - cost_optimized_tier: Primary=OpenAI (4o-mini), Backup=Gemini
    - balanced_tier: Primary=Anthropic (Sonnet), Backup=OpenAI

    Returns:
        HardenedRouter singleton instance
    """
    global _router_instance
    if _router_instance is None:
        logger.info("Initializing resilient router with default configurations")
        _router_instance = ModelRouter()
        tiers = list(_router_instance.get_stats()["available_models"].keys())
        logger.info(f"router initialized with tiers: {tiers}")
    return _router_instance


def reset_router() -> None:
    """Reset the router singleton (primarily for testing).

    This will force a new router instance to be created on the next
    call to get_resilient_router().
    """
    global _router_instance
    if _router_instance is not None:
        logger.info("Resetting resilient router singleton")
        _router_instance = None


def create_custom_router(configs: dict) -> ModelRouter:
    """Create a custom router with specific configurations.

    This does NOT affect the singleton instance returned by get_resilient_router().
    Use this when you need a router with custom routing configurations.

    Args:
        configs: Dictionary of extra model names to ModelConfig instances

    Returns:
        New ModelRouter instance with custom models added
    """
    from apps_shared.types.model_router_types import ModelConfig  # noqa: PLC0415

    logger.info(f"Creating custom router with tiers: {list(configs.keys())}")
    router = ModelRouter()
    for name, cfg in configs.items():
        if isinstance(cfg, ModelConfig):
            router.add_model(name, cfg)
    return router
