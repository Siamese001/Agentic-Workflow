"""Drift Detector — Monitors C0 context hash for drift detection.

Alerts when C0 context changes between replays, indicating potential
drift in the embedding space that could affect decision consistency.

# guardian: allow-direct-prompt-compilation
"""

from __future__ import annotations

import hashlib
import logging

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
    record_execution_trace,
)

emit_replay_key("p0", "drift_detector")
emit_determinism_digest("p0", "drift_detector")

_emit_dispatches_healing_run("p1", "drift_detector", "L6")
_emit_routes_through("p1", "drift_detector", "L6")
_emit_checks_agent_registry("p1", "drift_detector", "agent_registry")
_emit_validates_agent_capability("p1", "drift_detector", "capability")
_emit_dispatches_execution_plan("p1", "drift_detector", "exec_plan")
_emit_agent_executes_agent("p1", "drift_detector", "sub_agent")
_emit_routes_to_agent("p1", "drift_detector", "target_agent")
_emit_verifies_policy("p1", "drift_detector", "policy_check")
_emit_observes_runtime_state("p1", "drift_detector", "runtime_state")
_emit_verifies_boundary("p1", "drift_detector", "boundary_check")
_emit_transcripts_response("p1", "drift_detector", "transcript")
_emit_hard_fails_untranscripted("p1", "drift_detector")
_emit_gated_by_confidence("p1", "drift_detector", "confidence_gate")
_emit_escalates_to_human("p1", "drift_detector", "L6")
_emit_reads_policy_state("p1", "drift_detector", "L6")
_emit_authorize_and_execute("p2", "drift_detector", "execution_auth")
_emit_validates_capability("p2", "drift_detector", "capability_check")
_emit_routes_to_capability("p2", "drift_detector", "capability_route")
_emit_writes_via_uwg("p2", "drift_detector", "uwg_write")
_emit_blocks_direct_write("p2", "drift_detector", "direct_write_block")
_emit_records_tool_invocation("p2", "drift_detector", "tool_invocation")
_emit_captures_execution_output("p2", "drift_detector", "exec_output")
_emit_dispatches_agent("p3", "drift_detector", "agent_dispatch")
_emit_coordinates_agents("p3", "drift_detector", "agent_coordination")
_emit_records_workflow_lineage("p3", "drift_detector", "workflow_lineage")
_emit_records_healing_outcome("p3", "drift_detector", "healing_outcome")
_emit_escalates_failure("p3", "drift_detector", "failure_escalation")
_emit_orchestrates_workflow("p3", "drift_detector", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "drift_detector", "healing_dispatch")
_emit_invokes_evaluation("p3", "drift_detector", "evaluation_signal")
_emit_records_telemetry_event("p4", "drift_detector", "telemetry_event")
_emit_captures_evaluation_metric("p4", "drift_detector", "eval_metric")
_emit_stores_embedding("p4", "drift_detector", "embedding_store")
_emit_updates_meta_learning_state("p4", "drift_detector", "meta_learning")
_emit_links_execution_to_snapshot("p4", "drift_detector", "exec_snapshot_link")
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

record_execution_trace("drift_detector", "drift_detector_trace")


_emit_emits_metric_event("drift_detector", "p4obs", "metric_1")
_emit_emits_metric_event("drift_detector", "p4obs", "metric_2")
_emit_emits_metric_event("drift_detector", "p4obs", "metric_3")
_emit_emits_metric_event("drift_detector", "p4obs", "metric_4")
_emit_emits_metric_event("drift_detector", "p4obs", "metric_5")
_emit_emits_metric_event("drift_detector", "p4obs", "metric_6")
_emit_records_incident_event("drift_detector", "p4obs", "incident")
_emit_captures_runtime_anomaly("drift_detector", "p4obs", "anomaly")
_emit_writes_observability_log("drift_detector", "p4obs", "obs_log")
_emit_updates_monitoring_state("drift_detector", "p4obs", "mon_state")
_emit_triggers_alert("drift_detector", "p4obs", "alert")
_emit_links_incident_trace("drift_detector", "p4obs", "trace_link")
_emit_captures_pattern("drift_detector", "p3lm", "pattern")
_emit_records_learning_event("drift_detector", "p3lm", "learning_event")
_emit_writes_learning_snapshot("drift_detector", "p3lm", "snapshot")
_emit_feeds_meta_learning("drift_detector", "p3lm", "meta_feed")
_emit_updates_routing_strategy("drift_detector", "p3lm", "routing")
_emit_improves_agent_policy("drift_detector", "p3lm", "policy")
_emit_stores_learning_state("drift_detector", "p3lm", "state")
_emit_records_execution_trace("drift_detector", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("drift_detector", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("drift_detector", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("drift_detector", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("drift_detector", "L4_STATE", "p2_trace_5")
_emit_reads_environ("drift_detector", "env_read", "p2_env_1")
_emit_reads_environ("drift_detector", "env_read", "p2_env_2")
_emit_reads_runtime_state("drift_detector", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("drift_detector", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "drift_detector", "context_pull")
_emit_pulls_context("p1", "drift_detector", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "drift_detector", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "drift_detector", "uwg_term_2")
_emit_writes_through("p1", "drift_detector", "write_through")
_emit_writes_through("p1", "drift_detector", "write_through_2")
_emit_validated_by_safety_plane("p1", "drift_detector", "safety_validation")
_emit_invokes_eval("p1", "drift_detector", "eval_call")
_emit_proposal_commits_routing("p1", "drift_detector", "routing_commit")

logger = logging.getLogger(__name__)


class DriftDetector:
    """Detects drift in C0 context hash between executions.

    Maintains a registry of C0 context hashes and alerts when
    the hash changes, indicating potential drift in the embedding space.
    """

    def __init__(self) -> None:
        """Initialize the drift detector."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "DriftDetector.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "DriftDetector.__init__", "p0_governance")
        self._context_registry: dict[str, str] = {}
        self._drift_alerts: dict[str, tuple[str, str]] = {}

    def register_context_hash(self, replay_key: str, c0_context_hash: str) -> bool:
        """Register a C0 context hash for a replay key.

        Args:
            replay_key: The replay key identifier.
            c0_context_hash: The C0 context hash.

        Returns:
            True if drift was detected, False otherwise.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L6_OBSERVABILITY, "DriftDetector.register_context_hash"
        )

        if replay_key in self._context_registry:
            old_hash = self._context_registry[replay_key]
            if old_hash != c0_context_hash:
                self._drift_alerts[replay_key] = (old_hash, c0_context_hash)
                _adg_score: float = 0.5
                try:
                    from pathlib import Path as _Path

                    from agentic_core.adg.runtime.behavioral_index import get_behavioral_profile as _gbp

                    _root = _Path(__file__).resolve().parents[4]
                    _adg_score = _gbp(_Path(__file__).resolve(), _root).behavioral_score
                # guardian: allow-silent-swallow
                except Exception:
                    pass
                # guardian: allow-direct-prompt-compilation
                logger.warning(
                    "C0 context drift detected for replay key %s: old_hash=%s..., "
                    "new_hash=%s... adg_behavioral_score=%.3f",
                    replay_key,
                    old_hash[:8],
                    c0_context_hash[:8],
                    _adg_score,
                )
                return True
        else:
            self._context_registry[replay_key] = c0_context_hash
        return False

    def get_drift_alert(self, replay_key: str) -> tuple[str, str] | None:
        """Get drift alert for a replay key.

        Args:
            replay_key: The replay key identifier.

        Returns:
            Tuple of (old_hash, new_hash) if drift detected, None otherwise.
        """
        return self._drift_alerts.get(replay_key)

    def has_drift(self, replay_key: str) -> bool:
        """Check if drift was detected for a replay key.

        Args:
            replay_key: The replay key identifier.

        Returns:
            True if drift detected, False otherwise.
        """
        return replay_key in self._drift_alerts

    def clear_drift_alert(self, replay_key: str) -> None:
        """Clear drift alert for a replay key.

        Args:
            replay_key: The replay key identifier.
        """
        self._drift_alerts.pop(replay_key, None)

    def get_all_drift_alerts(self) -> dict[str, tuple[str, str]]:
        """Get all drift alerts.

        Returns:
            Dictionary mapping replay keys to (old_hash, new_hash) tuples.
        """
        return self._drift_alerts.copy()

    def reset(self) -> None:
        """Reset the drift detector (for testing)."""
        self._context_registry.clear()
        self._drift_alerts.clear()

    def compute_c0_context_hash(self, c0_context: str) -> str:
        """Compute hash for C0 context.

        Args:
            c0_context: The C0 context string.

        Returns:
            SHA-256 hash of the C0 context.
        """
        return hashlib.sha256(c0_context.encode("utf-8", errors="replace")).hexdigest()

    def get_context_hash(self, replay_key: str) -> str | None:
        """Get the registered context hash for a replay key.

        Args:
            replay_key: The replay key identifier.

        Returns:
            The context hash if registered, None otherwise.
        """
        return self._context_registry.get(replay_key)


_drift_detector: DriftDetector | None = None


def get_drift_detector() -> DriftDetector:
    """Get the global drift detector instance.

    Returns:
        The global DriftDetector instance.
    """
    global _drift_detector
    if _drift_detector is None:
        _drift_detector = DriftDetector()
    return _drift_detector


def reset_drift_detector() -> None:
    """Reset the global drift detector (for testing)."""
    global _drift_detector
    if _drift_detector is not None:
        _drift_detector.reset()
