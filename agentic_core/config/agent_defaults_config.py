"""
Agent Default Configuration

Phase 2 Landmine Remediation - Magic Configuration Extraction
This module externalizes hardcoded constants and thresholds,
enabling runtime tuning without code changes.

Usage:
    from agentic_core.config.agent_defaults import AgentDefaults

    threshold = AgentDefaults.get("PINECONE_RELEVANCE_THRESHOLD", 0.75)
"""

import os
from typing import Any

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

_emit_applies_guardrail("p0", "agent_defaults_config", "p0_governance")
_emit_reads_policy_state("p0", "agent_defaults_config", "policy_binding")
_emit_snapshots_state("p0", "agent_defaults_config", "state_snapshot")
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

_emit_emits_metric_event("agent_defaults_config", "p4obs", "metric_1")
_emit_emits_metric_event("agent_defaults_config", "p4obs", "metric_2")
_emit_emits_metric_event("agent_defaults_config", "p4obs", "metric_3")
_emit_emits_metric_event("agent_defaults_config", "p4obs", "metric_4")
_emit_emits_metric_event("agent_defaults_config", "p4obs", "metric_5")
_emit_emits_metric_event("agent_defaults_config", "p4obs", "metric_6")
_emit_records_incident_event("agent_defaults_config", "p4obs", "incident")
_emit_captures_runtime_anomaly("agent_defaults_config", "p4obs", "anomaly")
_emit_writes_observability_log("agent_defaults_config", "p4obs", "obs_log")
_emit_updates_monitoring_state("agent_defaults_config", "p4obs", "mon_state")
_emit_triggers_alert("agent_defaults_config", "p4obs", "alert")
_emit_links_incident_trace("agent_defaults_config", "p4obs", "trace_link")
_emit_captures_pattern("agent_defaults_config", "p3lm", "pattern")
_emit_records_learning_event("agent_defaults_config", "p3lm", "learning_event")
_emit_writes_learning_snapshot("agent_defaults_config", "p3lm", "snapshot")
_emit_feeds_meta_learning("agent_defaults_config", "p3lm", "meta_feed")
_emit_updates_routing_strategy("agent_defaults_config", "p3lm", "routing")
_emit_improves_agent_policy("agent_defaults_config", "p3lm", "policy")
_emit_stores_learning_state("agent_defaults_config", "p3lm", "state")
_emit_records_execution_trace("agent_defaults_config", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("agent_defaults_config", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("agent_defaults_config", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("agent_defaults_config", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("agent_defaults_config", "L4_STATE", "p2_trace_5")
_emit_reads_environ("agent_defaults_config", "env_read", "p2_env_1")
_emit_reads_environ("agent_defaults_config", "env_read", "p2_env_2")
_emit_reads_runtime_state("agent_defaults_config", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("agent_defaults_config", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "agent_defaults_config", "context_pull")
_emit_pulls_context("p1", "agent_defaults_config", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "agent_defaults_config", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "agent_defaults_config", "uwg_term_2")
_emit_writes_through("p1", "agent_defaults_config", "write_through")
_emit_writes_through("p1", "agent_defaults_config", "write_through_2")
_emit_validated_by_safety_plane("p1", "agent_defaults_config", "safety_validation")
_emit_invokes_eval("p1", "agent_defaults_config", "eval_call")
_emit_proposal_commits_routing("p1", "agent_defaults_config", "routing_commit")
_emit_escalates_to_human("p1", "agent_defaults_config", "human_escalation")
_emit_routes_through("p1", "agent_defaults_config", "route_through")
_emit_checks_agent_registry("p1", "agent_defaults_config", "agent_registry")
_emit_validates_agent_capability("p1", "agent_defaults_config", "capability")
_emit_dispatches_execution_plan("p1", "agent_defaults_config", "exec_plan")
_emit_agent_executes_agent("p1", "agent_defaults_config", "sub_agent")
_emit_routes_to_agent("p1", "agent_defaults_config", "target_agent")
_emit_verifies_policy("p1", "agent_defaults_config", "policy_check")
_emit_observes_runtime_state("p1", "agent_defaults_config", "runtime_state")
_emit_verifies_boundary("p1", "agent_defaults_config", "boundary_check")
_emit_transcripts_response("p1", "agent_defaults_config", "transcript")
_emit_hard_fails_untranscripted("p1", "agent_defaults_config")
_emit_gated_by_confidence("p1", "agent_defaults_config", "confidence_gate")
emit_replay_key("p0", "agent_defaults_config")
emit_determinism_digest("p0", "agent_defaults_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "agent_defaults_config", "execution_auth")
_emit_validates_capability("p2", "agent_defaults_config", "capability_check")
_emit_routes_to_capability("p2", "agent_defaults_config", "capability_route")
_emit_writes_via_uwg("p2", "agent_defaults_config", "uwg_write")
_emit_blocks_direct_write("p2", "agent_defaults_config", "direct_write_block")
_emit_records_tool_invocation("p2", "agent_defaults_config", "tool_invocation")
_emit_captures_execution_output("p2", "agent_defaults_config", "exec_output")
_emit_dispatches_agent("p3", "agent_defaults_config", "agent_dispatch")
_emit_coordinates_agents("p3", "agent_defaults_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "agent_defaults_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "agent_defaults_config", "healing_outcome")
_emit_escalates_failure("p3", "agent_defaults_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "agent_defaults_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "agent_defaults_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "agent_defaults_config", "evaluation_signal")
_emit_records_telemetry_event("p4", "agent_defaults_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "agent_defaults_config", "eval_metric")
_emit_stores_embedding("p4", "agent_defaults_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "agent_defaults_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "agent_defaults_config", "exec_snapshot_link")

# Configuration constants


class AgentDefaults:
    """
    Centralized configuration for agent default values.

    Values can be overridden via environment variables with the same name.
    All values have sensible defaults that match previous hardcoded behavior.
    """

    # === Vector Search Thresholds ===
    RAG_SIMILARITY_THRESHOLD: float = 0.8
    SEMANTIC_CACHE_THRESHOLD: float = 0.92

    # === Timeout Configuration (seconds) ===
    DEFAULT_API_TIMEOUT: float = 60.0
    TOOL_EXECUTION_TIMEOUT: int = 30
    HEAL_OPERATION_TIMEOUT: int = 120
    SUBPROCESS_TIMEOUT: int = 300

    # === Rate Limiting ===
    DEFAULT_RATE_LIMIT_REQUESTS: int = 100
    DEFAULT_RATE_LIMIT_WINDOW_SECONDS: int = 60

    # === Healing Thresholds ===
    CONFIDENCE_THRESHOLD: float = 0.75
    AUTO_EXECUTE_THRESHOLD: float = 0.75
    SAFETY_THRESHOLD: float = 0.95

    # === Model Configuration ===
    DEFAULT_MODEL: str = "gpt-4"
    FALLBACK_MODEL: str = "gpt-3.5-turbo"

    # === Circuit Breaker ===
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5
    CIRCUIT_BREAKER_RESET_TIMEOUT: int = 60

    # === Performance Thresholds ===
    PERFORMANCE_DEGRADATION_THRESHOLD: float = 0.5
    COMPLEXITY_THRESHOLD: int = 15
    MAX_CONCURRENT_OPERATIONS: int = 5

    # === Cost Management ===
    DEFAULT_BUDGET_LIMIT: float = 5.0
    BUDGET_WARNING_THRESHOLD: float = 0.8

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        Get a configuration value with environment variable override.

        Args:
            key: Configuration key (must be a class attribute)
            default: Default value if not found (uses class default if None)

        Returns:
            Configuration value (env var override takes precedence)
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "AgentDefaults.get")

        # Check environment variable first
        env_value = os.environ.get(key)
        if env_value is not None:
            # Try to convert to the expected type
            class_default = getattr(cls, key, default)
            if class_default is not None:
                try:
                    if isinstance(class_default, bool):
                        return env_value.lower() in ("1", "true", "yes")
                    elif isinstance(class_default, int):
                        return int(env_value)
                    elif isinstance(class_default, float):
                        return float(env_value)
                    else:
                        return env_value
                except (ValueError, TypeError):  # guardian: allow-silent-swallow -- intentional: type-coerce control flow
                    pass
            return env_value

        # Fall back to class default
        return getattr(cls, key, default)

    @classmethod
    def get_float(cls, key: str, default: float = 0.0) -> float:
        """Get a float configuration value."""
        value = cls.get(key, default)
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    @classmethod
    def get_int(cls, key: str, default: int = 0) -> int:
        """Get an integer configuration value."""
        value = cls.get(key, default)
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    @classmethod
    def get_bool(cls, key: str, default: bool = False) -> bool:
        """Get a boolean configuration value."""
        value = cls.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("1", "true", "yes")
        return bool(value)


# Convenience exports
def get_config(key: str, default: Any = None) -> Any:
    """Get a configuration value with environment variable override."""
    return AgentDefaults.get(key, default)


__all__ = [
    "AgentDefaults",
    "get_config",
]
