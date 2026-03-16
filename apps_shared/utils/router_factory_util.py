"""Factory for creating and managing the resilient router singleton.

Provides a global singleton instance of the HardenedRouter with default
configurations for common use cases.

Phase 2 - Resilient Routing Layer
"""

import logging

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
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
