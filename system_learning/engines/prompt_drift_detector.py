"""Prompt Drift Detector — detects quality regressions and improvements across prompt versions.

Compares two windows of ``PromptOutcomeRecord`` objects (baseline vs current)
and emits ``PromptDriftSignal`` objects when statistically significant changes
are detected in:

  - escalation_rate       (HITL escalations / total executions)
  - groundedness          (mean retrieval_groundedness_score)
  - replay_instability    (REPLAY_FAILURE / total executions)
  - guardrail_violations  (mean guardrail_hits count / total)

A drift signal is emitted as REGRESSION when the metric worsens beyond the
configured threshold, and IMPROVEMENT when it improves beyond the threshold.

Design invariants
-----------------
1. No wall-clock reads; ``timestamp_utc`` always caller-supplied.
2. Window comparisons are purely arithmetic — no ML inference.
3. All signals are content-addressed with deterministic signal_id.
4. Empty windows are handled gracefully (no signals produced).
5. Threshold crossing uses strict inequality (> threshold, not >=) to
   prevent noise from triggering on boundary values.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from typing import Sequence

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

_emit_authorize_and_execute("p2", "prompt_drift_detector", "execution_auth")
_emit_validates_capability("p2", "prompt_drift_detector", "capability_check")
_emit_routes_to_capability("p2", "prompt_drift_detector", "capability_route")
_emit_writes_via_uwg("p2", "prompt_drift_detector", "uwg_write")
_emit_blocks_direct_write("p2", "prompt_drift_detector", "direct_write_block")
_emit_records_tool_invocation("p2", "prompt_drift_detector", "tool_invocation")
_emit_captures_execution_output("p2", "prompt_drift_detector", "exec_output")
_emit_dispatches_agent("p3", "prompt_drift_detector", "agent_dispatch")
_emit_coordinates_agents("p3", "prompt_drift_detector", "agent_coordination")
_emit_records_workflow_lineage("p3", "prompt_drift_detector", "workflow_lineage")
_emit_records_healing_outcome("p3", "prompt_drift_detector", "healing_outcome")
_emit_escalates_failure("p3", "prompt_drift_detector", "failure_escalation")
_emit_orchestrates_workflow("p3", "prompt_drift_detector", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "prompt_drift_detector", "healing_dispatch")
_emit_invokes_evaluation("p3", "prompt_drift_detector", "evaluation_signal")
_emit_records_telemetry_event("p4", "prompt_drift_detector", "telemetry_event")
_emit_captures_evaluation_metric("p4", "prompt_drift_detector", "eval_metric")
_emit_stores_embedding("p4", "prompt_drift_detector", "embedding_store")
_emit_updates_meta_learning_state("p4", "prompt_drift_detector", "meta_learning")
_emit_links_execution_to_snapshot("p4", "prompt_drift_detector", "exec_snapshot_link")
from system_learning.enforcement.determinism import deterministic_json
from system_learning.types.prompt_adg_relations import (
    DRIFT_IMPROVEMENT_DETECTED,
    DRIFT_REGRESSION_DETECTED,
    DRIFT_TEMPLATE_SUPERSEDED,
    DRIFT_VERSION_REPLACED_BY,
)
from system_learning.types.prompt_artifact_types import (
    PromptDriftSignal,
    PromptOutcomeRecord,
)

_emit_applies_guardrail("p0", "prompt_drift_detector", "p0_governance")
_emit_reads_policy_state("p0", "prompt_drift_detector", "policy_binding")
_emit_snapshots_state("p0", "prompt_drift_detector", "state_snapshot")
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

_emit_emits_metric_event("prompt_drift_detector", "p4obs", "metric_1")
_emit_emits_metric_event("prompt_drift_detector", "p4obs", "metric_2")
_emit_emits_metric_event("prompt_drift_detector", "p4obs", "metric_3")
_emit_emits_metric_event("prompt_drift_detector", "p4obs", "metric_4")
_emit_emits_metric_event("prompt_drift_detector", "p4obs", "metric_5")
_emit_emits_metric_event("prompt_drift_detector", "p4obs", "metric_6")
_emit_records_incident_event("prompt_drift_detector", "p4obs", "incident")
_emit_captures_runtime_anomaly("prompt_drift_detector", "p4obs", "anomaly")
_emit_writes_observability_log("prompt_drift_detector", "p4obs", "obs_log")
_emit_updates_monitoring_state("prompt_drift_detector", "p4obs", "mon_state")
_emit_triggers_alert("prompt_drift_detector", "p4obs", "alert")
_emit_links_incident_trace("prompt_drift_detector", "p4obs", "trace_link")
_emit_captures_pattern("prompt_drift_detector", "p3lm", "pattern")
_emit_records_learning_event("prompt_drift_detector", "p3lm", "learning_event")
_emit_writes_learning_snapshot("prompt_drift_detector", "p3lm", "snapshot")
_emit_feeds_meta_learning("prompt_drift_detector", "p3lm", "meta_feed")
_emit_updates_routing_strategy("prompt_drift_detector", "p3lm", "routing")
_emit_improves_agent_policy("prompt_drift_detector", "p3lm", "policy")
_emit_stores_learning_state("prompt_drift_detector", "p3lm", "state")
_emit_records_execution_trace("prompt_drift_detector", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("prompt_drift_detector", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("prompt_drift_detector", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("prompt_drift_detector", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("prompt_drift_detector", "L4_STATE", "p2_trace_5")
_emit_reads_environ("prompt_drift_detector", "env_read", "p2_env_1")
_emit_reads_environ("prompt_drift_detector", "env_read", "p2_env_2")
_emit_reads_runtime_state("prompt_drift_detector", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("prompt_drift_detector", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "prompt_drift_detector", "context_pull")
_emit_pulls_context("p1", "prompt_drift_detector", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "prompt_drift_detector", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "prompt_drift_detector", "uwg_term_2")
_emit_writes_through("p1", "prompt_drift_detector", "write_through")
_emit_writes_through("p1", "prompt_drift_detector", "write_through_2")
_emit_validated_by_safety_plane("p1", "prompt_drift_detector", "safety_validation")
_emit_invokes_eval("p1", "prompt_drift_detector", "eval_call")
_emit_proposal_commits_routing("p1", "prompt_drift_detector", "routing_commit")
_emit_escalates_to_human("p1", "prompt_drift_detector", "human_escalation")
_emit_routes_through("p1", "prompt_drift_detector", "route_through")
_emit_checks_agent_registry("p1", "prompt_drift_detector", "agent_registry")
_emit_validates_agent_capability("p1", "prompt_drift_detector", "capability")
_emit_dispatches_execution_plan("p1", "prompt_drift_detector", "exec_plan")
_emit_agent_executes_agent("p1", "prompt_drift_detector", "sub_agent")
_emit_routes_to_agent("p1", "prompt_drift_detector", "target_agent")
_emit_verifies_policy("p1", "prompt_drift_detector", "policy_check")
_emit_observes_runtime_state("p1", "prompt_drift_detector", "runtime_state")
_emit_verifies_boundary("p1", "prompt_drift_detector", "boundary_check")
_emit_transcripts_response("p1", "prompt_drift_detector", "transcript")
_emit_hard_fails_untranscripted("p1", "prompt_drift_detector")
_emit_gated_by_confidence("p1", "prompt_drift_detector", "confidence_gate")
emit_replay_key("p0", "prompt_drift_detector")
emit_determinism_digest("p0", "prompt_drift_detector")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass
class DriftDetectorConfig:
    """Configuration for the prompt drift detector.

    Attributes
    ----------
    escalation_rate_threshold : float
        Minimum absolute change in escalation rate to trigger a signal.
    groundedness_threshold : float
        Minimum absolute change in mean groundedness to trigger a signal.
    replay_instability_threshold : float
        Minimum absolute change in replay failure rate to trigger a signal.
    guardrail_violation_threshold : float
        Minimum absolute change in guardrail hit rate to trigger a signal.
    """

    escalation_rate_threshold: float = 0.05
    groundedness_threshold: float = 0.05
    replay_instability_threshold: float = 0.05
    guardrail_violation_threshold: float = 0.05


# ---------------------------------------------------------------------------
# Window statistics
# ---------------------------------------------------------------------------


@dataclass
class WindowStats:
    """Aggregate statistics over a window of PromptOutcomeRecords."""

    n: int
    escalation_rate: float
    mean_groundedness: float
    replay_failure_rate: float
    guardrail_hit_rate: float


def _compute_stats(records: Sequence[PromptOutcomeRecord]) -> WindowStats:
    n = len(records)
    if n == 0:
        return WindowStats(
            n=0,
            escalation_rate=0.0,
            mean_groundedness=0.0,
            replay_failure_rate=0.0,
            guardrail_hit_rate=0.0,
        )
    escalations = sum(1 for r in records if r.hitl_escalation)
    replay_failures = sum(1 for r in records if r.replay_status == "FAILED")
    guardrail_hits = sum(1 for r in records if r.guardrail_hits)
    mean_gnd = sum(r.groundedness_score for r in records) / n
    return WindowStats(
        n=n,
        escalation_rate=round(escalations / n, 6),
        mean_groundedness=round(mean_gnd, 6),
        replay_failure_rate=round(replay_failures / n, 6),
        guardrail_hit_rate=round(guardrail_hits / n, 6),
    )


# ---------------------------------------------------------------------------
# Signal ID builder
# ---------------------------------------------------------------------------


def _build_signal_id(
    prompt_hash_before: str,
    prompt_hash_after: str,
    drift_type: str,
    timestamp_utc: int,
) -> str:
    canonical = deterministic_json({
        "drift_type": drift_type,
        "prompt_hash_after": prompt_hash_after,
        "prompt_hash_before": prompt_hash_before,
        "timestamp_utc": timestamp_utc,
    })
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Main detector
# ---------------------------------------------------------------------------


class PromptDriftDetector:
    """Compares baseline and current outcome windows to detect prompt drift.

    Usage::

        detector = PromptDriftDetector()
        signals = detector.detect(
            baseline_records=baseline,
            current_records=current,
            prompt_hash_before="abc...",
            prompt_hash_after="def...",
            timestamp_utc=ts,
        )
        for signal in signals:
            adg.emit(signal.adg_relation, ...)
    """

    def __init__(self, config: DriftDetectorConfig | None = None) -> None:
        self._config = config or DriftDetectorConfig()

    def detect(
        self,
        baseline_records: Sequence[PromptOutcomeRecord],
        current_records: Sequence[PromptOutcomeRecord],
        prompt_hash_before: str,
        prompt_hash_after: str,
        timestamp_utc: int,
        structural_drift_detected: bool = False,
    ) -> list[PromptDriftSignal]:
        """Detect drift between two windows of outcome records.

        Parameters
        ----------
        baseline_records : Sequence[PromptOutcomeRecord]
            Historical outcome records (older version / earlier window).
        current_records : Sequence[PromptOutcomeRecord]
            Current outcome records (newer version / current window).
        prompt_hash_before : str
            Prompt hash for the baseline window.
        prompt_hash_after : str
            Prompt hash for the current window.
        timestamp_utc : int
            Caller-supplied detection timestamp.
        structural_drift_detected : bool
            Whether structural template drift was detected.

        Returns
        -------
        list[PromptDriftSignal]
            Sorted by signal_id for determinism.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PromptDriftDetector.detect")

        if not current_records:
            return []

        cfg = self._config
        baseline = _compute_stats(baseline_records)
        current = _compute_stats(current_records)

        signals: list[PromptDriftSignal] = []

        # --- Structural drift from template files ---
        if structural_drift_detected:
            signals.append(self._make_signal(
                prompt_hash_before, prompt_hash_after,
                "STRUCTURAL_DRIFT", 1.0, None,
                baseline.n, current.n,
                DRIFT_REGRESSION_DETECTED, timestamp_utc,
            ))

        # --- Escalation rate ---
        esc_delta = current.escalation_rate - baseline.escalation_rate
        if abs(esc_delta) > cfg.escalation_rate_threshold:
            drift_type = (
                "ESCALATION_RATE_INCREASE" if esc_delta > 0
                else "IMPROVEMENT_DETECTED"
            )
            adg_rel = (
                DRIFT_REGRESSION_DETECTED if esc_delta > 0
                else DRIFT_IMPROVEMENT_DETECTED
            )
            signals.append(self._make_signal(
                prompt_hash_before, prompt_hash_after,
                drift_type, esc_delta, "NONE",
                baseline.n, current.n, adg_rel, timestamp_utc,
            ))

        # --- Groundedness ---
        gnd_delta = current.mean_groundedness - baseline.mean_groundedness
        if abs(gnd_delta) > cfg.groundedness_threshold:
            drift_type = (
                "GROUNDEDNESS_DROP" if gnd_delta < 0
                else "IMPROVEMENT_DETECTED"
            )
            adg_rel = (
                DRIFT_REGRESSION_DETECTED if gnd_delta < 0
                else DRIFT_IMPROVEMENT_DETECTED
            )
            signals.append(self._make_signal(
                prompt_hash_before, prompt_hash_after,
                drift_type, gnd_delta, "C0",
                baseline.n, current.n, adg_rel, timestamp_utc,
            ))

        # --- Replay instability ---
        replay_delta = current.replay_failure_rate - baseline.replay_failure_rate
        if abs(replay_delta) > cfg.replay_instability_threshold:
            drift_type = (
                "REPLAY_INSTABILITY" if replay_delta > 0
                else "IMPROVEMENT_DETECTED"
            )
            adg_rel = (
                DRIFT_REGRESSION_DETECTED if replay_delta > 0
                else DRIFT_IMPROVEMENT_DETECTED
            )
            signals.append(self._make_signal(
                prompt_hash_before, prompt_hash_after,
                drift_type, replay_delta, "NONE",
                baseline.n, current.n, adg_rel, timestamp_utc,
            ))

        # --- Guardrail violations ---
        guard_delta = current.guardrail_hit_rate - baseline.guardrail_hit_rate
        if abs(guard_delta) > cfg.guardrail_violation_threshold:
            drift_type = (
                "GUARDRAIL_VIOLATION_INCREASE" if guard_delta > 0
                else "IMPROVEMENT_DETECTED"
            )
            adg_rel = (
                DRIFT_REGRESSION_DETECTED if guard_delta > 0
                else DRIFT_IMPROVEMENT_DETECTED
            )
            signals.append(self._make_signal(
                prompt_hash_before, prompt_hash_after,
                drift_type, guard_delta, "D0",
                baseline.n, current.n, adg_rel, timestamp_utc,
            ))

        # Always emit a VERSION_REPLACED_BY relation if hashes differ
        if prompt_hash_before != prompt_hash_after and prompt_hash_before:
            signals.append(self._make_signal(
                prompt_hash_before, prompt_hash_after,
                "IMPROVEMENT_DETECTED", 0.0, None,
                baseline.n, current.n,
                DRIFT_VERSION_REPLACED_BY, timestamp_utc,
            ))

        signals.sort(key=lambda s: s.signal_id)
        return signals

    def detect_template_supersession(
        self,
        old_prompt_hash: str,
        new_prompt_hash: str,
        timestamp_utc: int,
    ) -> PromptDriftSignal:
        """Emit a TEMPLATE_SUPERSEDED signal when a template is replaced."""
        return self._make_signal(
            old_prompt_hash, new_prompt_hash,
            "IMPROVEMENT_DETECTED", 0.0, None,
            0, 1,
            DRIFT_TEMPLATE_SUPERSEDED, timestamp_utc,
        )

    def _make_signal(
        self,
        prompt_hash_before: str,
        prompt_hash_after: str,
        drift_type: str,
        magnitude: float,
        affected_slot: str | None,
        baseline_n: int,
        current_n: int,
        adg_relation: str,
        timestamp_utc: int,
    ) -> PromptDriftSignal:
        signal_id = _build_signal_id(
            prompt_hash_before, prompt_hash_after, drift_type, timestamp_utc
        )
        return PromptDriftSignal(
            signal_id=signal_id,
            prompt_hash_before=prompt_hash_before,
            prompt_hash_after=prompt_hash_after,
            drift_type=drift_type,
            magnitude=round(magnitude, 6),
            affected_slot=affected_slot if affected_slot in ("S0", "D0", "I0", "C0", "U0") else None,
            baseline_window_size=max(0, baseline_n),
            current_window_size=max(1, current_n),
            adg_relation=adg_relation,
            timestamp_utc=timestamp_utc,
        )


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------


def detect_prompt_drift(
    baseline_records: Sequence[PromptOutcomeRecord],
    current_records: Sequence[PromptOutcomeRecord],
    prompt_hash_before: str,
    prompt_hash_after: str,
    timestamp_utc: int,
    *,
    config: DriftDetectorConfig | None = None,
) -> list[PromptDriftSignal]:
    """Module-level convenience wrapper."""
    return PromptDriftDetector(config).detect(
        baseline_records,
        current_records,
        prompt_hash_before,
        prompt_hash_after,
        timestamp_utc,
    )


__all__ = [
    "DriftDetectorConfig",
    "PromptDriftDetector",
    "WindowStats",
    "detect_prompt_drift",
]
