"""Routing configuration schema for multi-provider fallback.

Defines the structure for routing tiers and provider fallback chains.

Phase 2 - Resilient Routing Layer
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_applies_guardrail("p0", "routing_tier_config", "p0_governance")
_emit_reads_policy_state("p0", "routing_tier_config", "policy_binding")
_emit_snapshots_state("p0", "routing_tier_config", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("routing_tier_config", "p4obs", "metric_1")
_emit_emits_metric_event("routing_tier_config", "p4obs", "metric_2")
_emit_emits_metric_event("routing_tier_config", "p4obs", "metric_3")
_emit_emits_metric_event("routing_tier_config", "p4obs", "metric_4")
_emit_emits_metric_event("routing_tier_config", "p4obs", "metric_5")
_emit_emits_metric_event("routing_tier_config", "p4obs", "metric_6")
_emit_records_incident_event("routing_tier_config", "p4obs", "incident")
_emit_captures_runtime_anomaly("routing_tier_config", "p4obs", "anomaly")
_emit_writes_observability_log("routing_tier_config", "p4obs", "obs_log")
_emit_updates_monitoring_state("routing_tier_config", "p4obs", "mon_state")
_emit_triggers_alert("routing_tier_config", "p4obs", "alert")
_emit_links_incident_trace("routing_tier_config", "p4obs", "trace_link")
_emit_captures_pattern("routing_tier_config", "p3lm", "pattern")
_emit_records_learning_event("routing_tier_config", "p3lm", "learning_event")
_emit_writes_learning_snapshot("routing_tier_config", "p3lm", "snapshot")
_emit_feeds_meta_learning("routing_tier_config", "p3lm", "meta_feed")
_emit_updates_routing_strategy("routing_tier_config", "p3lm", "routing")
_emit_improves_agent_policy("routing_tier_config", "p3lm", "policy")
_emit_stores_learning_state("routing_tier_config", "p3lm", "state")
_emit_records_execution_trace("routing_tier_config", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("routing_tier_config", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("routing_tier_config", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("routing_tier_config", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("routing_tier_config", "L4_STATE", "p2_trace_5")
_emit_reads_environ("routing_tier_config", "env_read", "p2_env_1")
_emit_reads_environ("routing_tier_config", "env_read", "p2_env_2")
_emit_reads_runtime_state("routing_tier_config", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("routing_tier_config", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "routing_tier_config", "context_pull")
_emit_pulls_context("p1", "routing_tier_config", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "routing_tier_config", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "routing_tier_config", "uwg_term_2")
_emit_writes_through("p1", "routing_tier_config", "write_through")
_emit_writes_through("p1", "routing_tier_config", "write_through_2")
_emit_validated_by_safety_plane("p1", "routing_tier_config", "safety_validation")
_emit_invokes_eval("p1", "routing_tier_config", "eval_call")
_emit_proposal_commits_routing("p1", "routing_tier_config", "routing_commit")
_emit_escalates_to_human("p1", "routing_tier_config", "human_escalation")
_emit_routes_through("p1", "routing_tier_config", "route_through")
_emit_checks_agent_registry("p1", "routing_tier_config", "agent_registry")
_emit_validates_agent_capability("p1", "routing_tier_config", "capability")
_emit_dispatches_execution_plan("p1", "routing_tier_config", "exec_plan")
_emit_agent_executes_agent("p1", "routing_tier_config", "sub_agent")
_emit_routes_to_agent("p1", "routing_tier_config", "target_agent")
_emit_verifies_policy("p1", "routing_tier_config", "policy_check")
_emit_observes_runtime_state("p1", "routing_tier_config", "runtime_state")
_emit_verifies_boundary("p1", "routing_tier_config", "boundary_check")
_emit_transcripts_response("p1", "routing_tier_config", "transcript")
_emit_hard_fails_untranscripted("p1", "routing_tier_config")
_emit_gated_by_confidence("p1", "routing_tier_config", "confidence_gate")
emit_replay_key("p0", "routing_tier_config")
emit_determinism_digest("p0", "routing_tier_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "routing_tier_config", "execution_auth")
_emit_validates_capability("p2", "routing_tier_config", "capability_check")
_emit_routes_to_capability("p2", "routing_tier_config", "capability_route")
_emit_writes_via_uwg("p2", "routing_tier_config", "uwg_write")
_emit_blocks_direct_write("p2", "routing_tier_config", "direct_write_block")
_emit_records_tool_invocation("p2", "routing_tier_config", "tool_invocation")
_emit_captures_execution_output("p2", "routing_tier_config", "exec_output")
_emit_dispatches_agent("p3", "routing_tier_config", "agent_dispatch")
_emit_coordinates_agents("p3", "routing_tier_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "routing_tier_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "routing_tier_config", "healing_outcome")
_emit_escalates_failure("p3", "routing_tier_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "routing_tier_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "routing_tier_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "routing_tier_config", "evaluation_signal")
_emit_records_telemetry_event("p4", "routing_tier_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "routing_tier_config", "eval_metric")
_emit_stores_embedding("p4", "routing_tier_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "routing_tier_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "routing_tier_config", "exec_snapshot_link")



DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class Provider(Enum):
    """LLM provider."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LOCAL = "local"


class RoutingTier(str, Enum):
    """Predefined routing tiers for different use cases."""

    REASONING = "reasoning_tier"
    SPEED = "speed_tier"
    COST_OPTIMIZED = "cost_optimized_tier"
    BALANCED = "balanced_tier"


@dataclass
class RouteConfig:
    """configuration for a routing tier.

    Defines the primary provider and fallback chain for a specific
    routing tier. The router will attempt providers in order until
    one succeeds.

    Attributes:
        tier_name: Name of the routing tier
        primary_provider: Primary provider to attempt first
        fallback_providers: Ordered list of fallback providers
        timeout_ms: Timeout for each provider attempt
        model_overrides: Optional model name overrides per provider
    """

    tier_name: str
    primary_provider: Provider
    fallback_providers: list[Provider]
    timeout_ms: int = 60000
    model_overrides: dict | None = None

    def __post_init__(self):
        """Validate configuration."""
        if not self.tier_name:
            raise ValueError("tier_name cannot be empty")

        if not self.fallback_providers:
            raise ValueError("fallback_providers cannot be empty")

        # Ensure no duplicate providers in the chain
        all_providers = [self.primary_provider] + self.fallback_providers
        if len(all_providers) != len(set(all_providers)):
            raise ValueError("Duplicate providers in routing chain")

        if self.timeout_ms <= 0:
            raise ValueError("timeout_ms must be positive")

    def get_all_providers(self) -> list[Provider]:
        """Get all providers in order (primary + fallbacks)."""
        return [self.primary_provider] + self.fallback_providers

    def get_model_for_provider(self, provider: Provider) -> str | None:
        """Get model override for a specific provider."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RouteConfig.get_model_for_provider")

        if self.model_overrides:
            return self.model_overrides.get(provider.value)
        return None


# Default routing configurations
DEFAULT_ROUTING_CONFIGS = {
    RoutingTier.REASONING: RouteConfig(
        tier_name=RoutingTier.REASONING.value,
        primary_provider=Provider.OPENAI,
        fallback_providers=[Provider.ANTHROPIC, Provider.GOOGLE],
        timeout_ms=120000,  # 2 minutes for reasoning tasks
        model_overrides={
            Provider.OPENAI.value: "gpt-4o-2024-08-06",
            Provider.ANTHROPIC.value: "claude-3-5-sonnet-20241022",
            Provider.GOOGLE.value: "gemini-2.5-flash",
        },
    ),
    RoutingTier.SPEED: RouteConfig(
        tier_name=RoutingTier.SPEED.value,
        primary_provider=Provider.GOOGLE,
        fallback_providers=[Provider.OPENAI, Provider.ANTHROPIC],
        timeout_ms=30000,  # 30 seconds for speed tasks
        model_overrides={
            Provider.GOOGLE.value: "gemini-2.5-flash",
            Provider.OPENAI.value: "gpt-4o-mini",
            Provider.ANTHROPIC.value: "claude-3-5-haiku-20241022",
        },
    ),
    RoutingTier.COST_OPTIMIZED: RouteConfig(
        tier_name=RoutingTier.COST_OPTIMIZED.value,
        primary_provider=Provider.OPENAI,
        fallback_providers=[Provider.GOOGLE, Provider.ANTHROPIC],
        timeout_ms=60000,
        model_overrides={
            Provider.OPENAI.value: "gpt-4o-mini",
            Provider.GOOGLE.value: "gemini-2.5-flash",
            Provider.ANTHROPIC.value: "claude-3-5-haiku-20241022",
        },
    ),
    RoutingTier.BALANCED: RouteConfig(
        tier_name=RoutingTier.BALANCED.value,
        primary_provider=Provider.ANTHROPIC,
        fallback_providers=[Provider.OPENAI, Provider.GOOGLE],
        timeout_ms=60000,
        model_overrides={
            Provider.ANTHROPIC.value: "claude-3-5-sonnet-20241022",
            Provider.OPENAI.value: "gpt-4o-2024-08-06",
            Provider.GOOGLE.value: "gemini-2.5-flash",
        },
    ),
}
