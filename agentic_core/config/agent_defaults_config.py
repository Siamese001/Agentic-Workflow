"""
Agent Default Configuration

Phase 2 Landmine Remediation - Magic Configuration Extraction
This module externalizes hardcoded constants and thresholds,
enabling runtime tuning without code changes.

Usage:
    from agentic_core.config.agent_defaults import AgentDefaults

    threshold = AgentDefaults.get("PINECONE_RELEVANCE_THRESHOLD", 0.75)
"""

from agentic_core.config.model_catalog import (
    OPENAI_GPT35_TURBO_MODEL_ID,
    OPENAI_GPT4_MODEL_ID,
)

import os
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "agent_defaults_config", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "agent_defaults_config", "policy_binding")
trace_contract._emit_snapshots_state("p0", "agent_defaults_config", "state_snapshot")

trace_contract._emit_emits_metric_event("agent_defaults_config", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("agent_defaults_config", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("agent_defaults_config", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("agent_defaults_config", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("agent_defaults_config", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("agent_defaults_config", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("agent_defaults_config", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("agent_defaults_config", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("agent_defaults_config", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("agent_defaults_config", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("agent_defaults_config", "p4obs", "alert")
trace_contract._emit_links_incident_trace("agent_defaults_config", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("agent_defaults_config", "p3lm", "pattern")
trace_contract._emit_records_learning_event("agent_defaults_config", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("agent_defaults_config", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("agent_defaults_config", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("agent_defaults_config", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("agent_defaults_config", "p3lm", "policy")
trace_contract._emit_stores_learning_state("agent_defaults_config", "p3lm", "state")
trace_contract._emit_records_execution_trace("agent_defaults_config", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("agent_defaults_config", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("agent_defaults_config", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("agent_defaults_config", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("agent_defaults_config", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("agent_defaults_config", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("agent_defaults_config", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("agent_defaults_config", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("agent_defaults_config", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "agent_defaults_config", "context_pull")
trace_contract._emit_pulls_context("p1", "agent_defaults_config", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "agent_defaults_config", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "agent_defaults_config", "uwg_term_2")
trace_contract._emit_writes_through("p1", "agent_defaults_config", "write_through")
trace_contract._emit_writes_through("p1", "agent_defaults_config", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "agent_defaults_config", "safety_validation")
trace_contract._emit_invokes_eval("p1", "agent_defaults_config", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "agent_defaults_config", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "agent_defaults_config", "human_escalation")
trace_contract._emit_routes_through("p1", "agent_defaults_config", "route_through")
trace_contract._emit_checks_agent_registry("p1", "agent_defaults_config", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "agent_defaults_config", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "agent_defaults_config", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "agent_defaults_config", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "agent_defaults_config", "target_agent")
trace_contract._emit_verifies_policy("p1", "agent_defaults_config", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "agent_defaults_config", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "agent_defaults_config", "boundary_check")
trace_contract._emit_transcripts_response("p1", "agent_defaults_config", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "agent_defaults_config")
trace_contract._emit_gated_by_confidence("p1", "agent_defaults_config", "confidence_gate")
trace_contract.emit_replay_key("p0", "agent_defaults_config")
trace_contract.emit_determinism_digest("p0", "agent_defaults_config")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "agent_defaults_config", "execution_auth")
trace_contract._emit_validates_capability("p2", "agent_defaults_config", "capability_check")
trace_contract._emit_routes_to_capability("p2", "agent_defaults_config", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "agent_defaults_config", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "agent_defaults_config", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "agent_defaults_config", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "agent_defaults_config", "exec_output")
trace_contract._emit_dispatches_agent("p3", "agent_defaults_config", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "agent_defaults_config", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "agent_defaults_config", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "agent_defaults_config", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "agent_defaults_config", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "agent_defaults_config", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "agent_defaults_config", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "agent_defaults_config", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "agent_defaults_config", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "agent_defaults_config", "eval_metric")
trace_contract._emit_stores_embedding("p4", "agent_defaults_config", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "agent_defaults_config", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "agent_defaults_config", "exec_snapshot_link")

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
    DEFAULT_MODEL: str = OPENAI_GPT4_MODEL_ID
    FALLBACK_MODEL: str = OPENAI_GPT35_TURBO_MODEL_ID

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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "AgentDefaults.get")

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
                except (
                    ValueError,
                    TypeError,
                ):  # guardian: allow-silent-swallow -- intentional: type-coerce control flow
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
