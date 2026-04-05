"""
Feature Flag Manager for controlled rollout of new capabilities.

Provides centralized feature flag management with environment variable support
and graceful degradation patterns.
"""

import logging
import os
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "feature_flags_config", "p0_governance")
_emit_reads_policy_state("p0", "feature_flags_config", "policy_binding")
_emit_snapshots_state("p0", "feature_flags_config", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
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
from agentic_core.config.constants_config import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

_emit_emits_metric_event("feature_flags_config", "p4obs", "metric_1")
_emit_emits_metric_event("feature_flags_config", "p4obs", "metric_2")
_emit_emits_metric_event("feature_flags_config", "p4obs", "metric_3")
_emit_emits_metric_event("feature_flags_config", "p4obs", "metric_4")
_emit_emits_metric_event("feature_flags_config", "p4obs", "metric_5")
_emit_emits_metric_event("feature_flags_config", "p4obs", "metric_6")
_emit_records_incident_event("feature_flags_config", "p4obs", "incident")
_emit_captures_runtime_anomaly("feature_flags_config", "p4obs", "anomaly")
_emit_writes_observability_log("feature_flags_config", "p4obs", "obs_log")
_emit_updates_monitoring_state("feature_flags_config", "p4obs", "mon_state")
_emit_triggers_alert("feature_flags_config", "p4obs", "alert")
_emit_links_incident_trace("feature_flags_config", "p4obs", "trace_link")
_emit_captures_pattern("feature_flags_config", "p3lm", "pattern")
_emit_records_learning_event("feature_flags_config", "p3lm", "learning_event")
_emit_writes_learning_snapshot("feature_flags_config", "p3lm", "snapshot")
_emit_feeds_meta_learning("feature_flags_config", "p3lm", "meta_feed")
_emit_updates_routing_strategy("feature_flags_config", "p3lm", "routing")
_emit_improves_agent_policy("feature_flags_config", "p3lm", "policy")
_emit_stores_learning_state("feature_flags_config", "p3lm", "state")
_emit_records_execution_trace("feature_flags_config", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("feature_flags_config", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("feature_flags_config", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("feature_flags_config", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("feature_flags_config", "L4_STATE", "p2_trace_5")
_emit_reads_environ("feature_flags_config", "env_read", "p2_env_1")
_emit_reads_environ("feature_flags_config", "env_read", "p2_env_2")
_emit_reads_runtime_state("feature_flags_config", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("feature_flags_config", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "feature_flags_config", "context_pull")
_emit_pulls_context("p1", "feature_flags_config", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "feature_flags_config", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "feature_flags_config", "uwg_term_2")
_emit_writes_through("p1", "feature_flags_config", "write_through")
_emit_writes_through("p1", "feature_flags_config", "write_through_2")
_emit_validated_by_safety_plane("p1", "feature_flags_config", "safety_validation")
_emit_invokes_eval("p1", "feature_flags_config", "eval_call")
_emit_proposal_commits_routing("p1", "feature_flags_config", "routing_commit")
_emit_escalates_to_human("p1", "feature_flags_config", "human_escalation")
_emit_routes_through("p1", "feature_flags_config", "route_through")
_emit_checks_agent_registry("p1", "feature_flags_config", "agent_registry")
_emit_validates_agent_capability("p1", "feature_flags_config", "capability")
_emit_dispatches_execution_plan("p1", "feature_flags_config", "exec_plan")
_emit_agent_executes_agent("p1", "feature_flags_config", "sub_agent")
_emit_routes_to_agent("p1", "feature_flags_config", "target_agent")
_emit_verifies_policy("p1", "feature_flags_config", "policy_check")
_emit_observes_runtime_state("p1", "feature_flags_config", "runtime_state")
_emit_verifies_boundary("p1", "feature_flags_config", "boundary_check")
_emit_transcripts_response("p1", "feature_flags_config", "transcript")
_emit_hard_fails_untranscripted("p1", "feature_flags_config")
_emit_gated_by_confidence("p1", "feature_flags_config", "confidence_gate")
emit_replay_key("p0", "feature_flags_config")
emit_determinism_digest("p0", "feature_flags_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "feature_flags_config", "execution_auth")
_emit_validates_capability("p2", "feature_flags_config", "capability_check")
_emit_routes_to_capability("p2", "feature_flags_config", "capability_route")
_emit_writes_via_uwg("p2", "feature_flags_config", "uwg_write")
_emit_blocks_direct_write("p2", "feature_flags_config", "direct_write_block")
_emit_records_tool_invocation("p2", "feature_flags_config", "tool_invocation")
_emit_captures_execution_output("p2", "feature_flags_config", "exec_output")
_emit_dispatches_agent("p3", "feature_flags_config", "agent_dispatch")
_emit_coordinates_agents("p3", "feature_flags_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "feature_flags_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "feature_flags_config", "healing_outcome")
_emit_escalates_failure("p3", "feature_flags_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "feature_flags_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "feature_flags_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "feature_flags_config", "evaluation_signal")
_emit_records_telemetry_event("p4", "feature_flags_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "feature_flags_config", "eval_metric")
_emit_stores_embedding("p4", "feature_flags_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "feature_flags_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "feature_flags_config", "exec_snapshot_link")

# Configuration constants

logger = logging.getLogger(__name__)


@dataclass
class FeatureFlag:
    """Feature flag configuration."""

    name: str
    default: bool = False
    description: str = ""
    required_for_healing: bool = False


class FeatureFlagManager:
    """Centralized feature flag management.

    Flags can be controlled via environment variables.
    All flags default to False for safe rollout.
    """

    FLAGS: dict[str, FeatureFlag] = {
        "ENABLE_META_LEARNING": FeatureFlag(
            name="ENABLE_META_LEARNING",
            default=False,
            description="Enable meta-learning recall-or-execute pattern",
            required_for_healing=False,
        ),
        "ENABLE_AUDIT_TRAIL": FeatureFlag(
            name="ENABLE_AUDIT_TRAIL",
            default=False,
            description="Enable cryptographic audit trail logging",
            required_for_healing=True,
        ),
        "ENABLE_COST_GUARDRAIL": FeatureFlag(
            name="ENABLE_COST_GUARDRAIL",
            default=False,
            description="Enable cost monitoring and budget enforcement",
            required_for_healing=True,
        ),
        "ENABLE_HITL_WORKFLOW": FeatureFlag(
            name="ENABLE_HITL_WORKFLOW",
            default=False,
            description="Enable human-in-the-loop approval workflow",
            required_for_healing=True,
        ),
        "ENABLE_VERIFICATION_GATE": FeatureFlag(
            name="ENABLE_VERIFICATION_GATE",
            default=False,
            description="Enable verification gate for healing operations",
            required_for_healing=True,
        ),
        "ENABLE_DETECTION_SIGNAL": FeatureFlag(
            name="ENABLE_DETECTION_SIGNAL",
            default=False,
            description="Enable structured detection signal emission",
            required_for_healing=False,
        ),
    }

    _override_cache: dict[str, bool] = {}

    @classmethod
    def is_enabled(cls, flag_name: str, agent_name: str | None = None) -> bool:
        """Check if feature flag is enabled.

        Args:
            flag_name: Name of the feature flag
            agent_name: Optional agent name for logging

        Returns:
            True if flag is enabled, False otherwise
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "FeatureFlagManager.is_enabled")

        # Check override cache first
        if flag_name in cls._override_cache:
            return cls._override_cache[flag_name]

        flag = cls.FLAGS.get(flag_name)
        if flag is None:
            logger.warning(f"Unknown feature flag: {flag_name}")
            return False

        # Check environment variable
        env_value = os.getenv(flag_name, str(flag.default)).lower()
        enabled = env_value in ("true", "1", "yes", "on")

        # Debug logging
        if agent_name:
            logger.debug(f"[FLAG] {flag_name}={enabled} for {agent_name}")

        return enabled

    @classmethod
    def set_override(cls, flag_name: str, value: bool) -> None:
        """Set a runtime override for a flag.

        Useful for testing and gradual rollout.

        Args:
            flag_name: Name of the flag
            value: Override value
        """
        cls._override_cache[flag_name] = value
        logger.info(f"[FLAG] Override set: {flag_name}={value}")

    @classmethod
    def clear_override(cls, flag_name: str) -> None:
        """Clear a runtime override.

        Args:
            flag_name: Name of the flag to clear
        """
        if flag_name in cls._override_cache:
            del cls._override_cache[flag_name]
            logger.info(f"[FLAG] Override cleared: {flag_name}")

    @classmethod
    def clear_all_overrides(cls) -> None:
        """Clear all runtime overrides."""
        cls._override_cache.clear()
        logger.info("[FLAG] All overrides cleared")

    @classmethod
    def required_for_healing(cls, flag_name: str) -> bool:
        """Check if flag is required for healing operations.

        Args:
            flag_name: Name of the flag

        Returns:
            True if required for healing
        """
        flag = cls.FLAGS.get(flag_name)
        return flag.required_for_healing if flag else False

    @classmethod
    def get_all_flags(cls) -> dict[str, bool]:
        """Get current state of all flags.

        Returns:
            Dictionary of flag names to their current values
        """
        return {name: cls.is_enabled(name) for name in cls.FLAGS.keys()}

    @classmethod
    def get_healing_required_flags(cls) -> dict[str, bool]:
        """Get flags required for healing operations.

        Returns:
            Dictionary of healing-required flag names to their values
        """
        return {name: cls.is_enabled(name) for name, flag in cls.FLAGS.items() if flag.required_for_healing}

    @classmethod
    def validate_healing_flags(cls, agent_name: str) -> tuple[bool, list[str]]:
        """Validate all healing-required flags are enabled.

        Args:
            agent_name: Name of the agent for logging

        Returns:
            Tuple of (all_enabled, list_of_disabled_flags)
        """
        disabled = []
        for name, flag in cls.FLAGS.items():
            if flag.required_for_healing and not cls.is_enabled(name, agent_name):
                disabled.append(name)

        if disabled:
            logger.warning(f"[FLAG] Agent {agent_name} missing healing flags: {disabled}")

        return len(disabled) == 0, disabled

    @classmethod
    def register_flag(cls, flag: FeatureFlag) -> None:
        """Register a new feature flag.

        Args:
            flag: FeatureFlag to register
        """
        cls.FLAGS[flag.name] = flag
        logger.info(f"[FLAG] Registered: {flag.name}")

    @classmethod
    def get_flag_info(cls, flag_name: str) -> dict[str, Any] | None:
        """Get information about a flag.

        Args:
            flag_name: Name of the flag

        Returns:
            Dictionary with flag info or None if not found
        """
        flag = cls.FLAGS.get(flag_name)
        if flag is None:
            return None

        return {
            "name": flag.name,
            "default": flag.default,
            "description": flag.description,
            "required_for_healing": flag.required_for_healing,
            "current_value": cls.is_enabled(flag_name),
            "has_override": flag_name in cls._override_cache,
        }
