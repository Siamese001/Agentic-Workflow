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

        Returns
        -------
        list[PromptDriftSignal]
            Sorted by signal_id for determinism.
        """
        if not current_records:
            return []

        cfg = self._config
        baseline = _compute_stats(baseline_records)
        current = _compute_stats(current_records)

        signals: list[PromptDriftSignal] = []

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
