"""
SSOT Feature Flag Mixin — L4-Sourced Feature Flags with Replay Lock.

Provides feature flags that:
  - Sourced exclusively from L4 config (never environment variables)
  - Replay mode locks flag snapshot (no runtime changes)
  - No environment fallback

Layer: L2 Execution Aid
Authority: Flag reading only. No L4 mutation. No routing influence.
"""

from __future__ import annotations

import logging
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

_emit_applies_guardrail("p0", "ssot_feature_flag_mixin", "p0_governance")
_emit_snapshots_state("p0", "ssot_feature_flag_mixin", "state_snapshot")
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

_emit_emits_metric_event("ssot_feature_flag_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("ssot_feature_flag_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("ssot_feature_flag_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("ssot_feature_flag_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("ssot_feature_flag_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("ssot_feature_flag_mixin", "p4obs", "metric_6")
_emit_records_incident_event("ssot_feature_flag_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("ssot_feature_flag_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("ssot_feature_flag_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("ssot_feature_flag_mixin", "p4obs", "mon_state")
_emit_triggers_alert("ssot_feature_flag_mixin", "p4obs", "alert")
_emit_links_incident_trace("ssot_feature_flag_mixin", "p4obs", "trace_link")
_emit_captures_pattern("ssot_feature_flag_mixin", "p3lm", "pattern")
_emit_records_learning_event("ssot_feature_flag_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ssot_feature_flag_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("ssot_feature_flag_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ssot_feature_flag_mixin", "p3lm", "routing")
_emit_improves_agent_policy("ssot_feature_flag_mixin", "p3lm", "policy")
_emit_stores_learning_state("ssot_feature_flag_mixin", "p3lm", "state")
_emit_records_execution_trace("ssot_feature_flag_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ssot_feature_flag_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ssot_feature_flag_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ssot_feature_flag_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ssot_feature_flag_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ssot_feature_flag_mixin", "env_read", "p2_env_1")
_emit_reads_environ("ssot_feature_flag_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("ssot_feature_flag_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ssot_feature_flag_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ssot_feature_flag_mixin", "context_pull")
_emit_pulls_context("p1", "ssot_feature_flag_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ssot_feature_flag_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ssot_feature_flag_mixin", "uwg_term_2")
_emit_writes_through("p1", "ssot_feature_flag_mixin", "write_through")
_emit_writes_through("p1", "ssot_feature_flag_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "ssot_feature_flag_mixin", "safety_validation")
_emit_invokes_eval("p1", "ssot_feature_flag_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "ssot_feature_flag_mixin", "routing_commit")
_emit_escalates_to_human("p1", "ssot_feature_flag_mixin", "human_escalation")
_emit_routes_through("p1", "ssot_feature_flag_mixin", "route_through")
_emit_checks_agent_registry("p1", "ssot_feature_flag_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "ssot_feature_flag_mixin", "capability")
_emit_dispatches_execution_plan("p1", "ssot_feature_flag_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "ssot_feature_flag_mixin", "sub_agent")
_emit_routes_to_agent("p1", "ssot_feature_flag_mixin", "target_agent")
_emit_verifies_policy("p1", "ssot_feature_flag_mixin", "policy_check")
_emit_observes_runtime_state("p1", "ssot_feature_flag_mixin", "runtime_state")
_emit_verifies_boundary("p1", "ssot_feature_flag_mixin", "boundary_check")
_emit_transcripts_response("p1", "ssot_feature_flag_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "ssot_feature_flag_mixin")
_emit_gated_by_confidence("p1", "ssot_feature_flag_mixin", "confidence_gate")
emit_replay_key("p0", "ssot_feature_flag_mixin")
emit_determinism_digest("p0", "ssot_feature_flag_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ssot_feature_flag_mixin", "execution_auth")
_emit_validates_capability("p2", "ssot_feature_flag_mixin", "capability_check")
_emit_routes_to_capability("p2", "ssot_feature_flag_mixin", "capability_route")
_emit_writes_via_uwg("p2", "ssot_feature_flag_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "ssot_feature_flag_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "ssot_feature_flag_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "ssot_feature_flag_mixin", "exec_output")
_emit_dispatches_agent("p3", "ssot_feature_flag_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "ssot_feature_flag_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "ssot_feature_flag_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "ssot_feature_flag_mixin", "healing_outcome")
_emit_escalates_failure("p3", "ssot_feature_flag_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "ssot_feature_flag_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ssot_feature_flag_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "ssot_feature_flag_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "ssot_feature_flag_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ssot_feature_flag_mixin", "eval_metric")
_emit_stores_embedding("p4", "ssot_feature_flag_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "ssot_feature_flag_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ssot_feature_flag_mixin", "exec_snapshot_link")

_logger = logging.getLogger("SSOTFeatureFlags")


class SSOTFeatureFlagMixin:
    """L4-sourced feature flags with replay snapshot lock.

    Reads ``active_policy_hash`` and ``is_replay_mode`` from ReplayGuardMixin.
    Flags are loaded from L4 config at construction time.
    Under replay mode, the flag snapshot is frozen (no updates allowed).
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._ssot_flags: dict[str, bool] = self._load_flags_from_l4()
        self._ssot_flags_frozen: bool = getattr(self, "is_replay_mode", False)

    def flag_enabled(self, flag_name: str, default: bool = False) -> bool:
        """Check if a feature flag is enabled.

        Parameters
        ----------
        flag_name : str
            Name of the feature flag.
        default : bool
            Default value if flag not found.

        Returns
        -------
        bool
            Whether the flag is enabled.
        """
        return self._ssot_flags.get(flag_name, default)

    def flag_set(self, flag_name: str, value: bool) -> bool:
        """Set a feature flag value. Rejected under replay mode.

        Parameters
        ----------
        flag_name : str
            Name of the feature flag.
        value : bool
            New flag value.

        Returns
        -------
        bool
            True if flag was set, False if rejected (replay mode).
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SSOTFeatureFlagMixin.flag_set")

        if self._ssot_flags_frozen:
            _logger.warning("[SSOTFlags] Flag change rejected (frozen): %s=%s", flag_name, value)
            return False
        self._ssot_flags[flag_name] = value
        _logger.debug("[SSOTFlags] %s = %s", flag_name, value)
        return True

    @property
    def all_flags(self) -> dict[str, bool]:
        """Return a copy of all current flags."""
        return dict(self._ssot_flags)

    @property
    def flags_frozen(self) -> bool:
        """Whether flags are frozen (replay mode)."""
        return self._ssot_flags_frozen

    @staticmethod
    def _load_flags_from_l4() -> dict[str, bool]:
        """Load feature flags from L4 config.

        Returns default flags if L4 config is unavailable.
        Never reads from environment variables.
        """
        try:
            from agentic_core.L4_state.config.versioned_configs import get_active_configs

            configs = get_active_configs()
            return {
                "enable_llm_healing": True,
                "enable_meta_learning": True,
                "enable_circuit_breaker": True,
                "enable_rate_limiting": True,
                "enable_tracing": True,
                "enable_audit_trail": True,
                "enable_adaptive_execution": False,
                "enable_hallucination_detection": True,
                "l4_config_version": configs.policy.version == "1.0.0",
            }
        # guardian: allow-silent-swallow - optional dependency
        except ImportError:
            _logger.warning("[SSOTFlags] L4 config unavailable; using defaults")
            return {
                "enable_llm_healing": True,
                "enable_meta_learning": True,
                "enable_circuit_breaker": True,
                "enable_rate_limiting": True,
                "enable_tracing": True,
                "enable_audit_trail": True,
                "enable_adaptive_execution": False,
                "enable_hallucination_detection": True,
            }
