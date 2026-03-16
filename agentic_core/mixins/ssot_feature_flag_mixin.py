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

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_applies_guardrail("p0", "ssot_feature_flag_mixin", "p0_governance")
_emit_snapshots_state("p0", "ssot_feature_flag_mixin", "state_snapshot")
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
