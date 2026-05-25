"""Signal Aggregator Engine — Evaluation Spine Component E.

Aggregates BUS P (Preferences/Grades) and BUS T (Telemetry/Trace) into unified
evaluation signals per the Evaluation Spine documentation.

Produces:
  - Score bundles
  - Decisiveness tags
  - Drift flags
  - Confidence/variance metrics
  - Severity classification

Deterministic, fail-closed, with full ADG traceability.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Literal

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_blocks_direct_write,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_records_execution_trace,
    _emit_records_tool_invocation,
    _emit_routes_to_agent,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)
from agentic_core.L6_system_learning.enforcement.determinism import deterministic_json, stable_sha256_json

# ADG wiring for signal aggregator engine
_emit_records_execution_trace("signal_aggregator_engine", "p0", "signal_aggregator_trace")
_emit_applies_guardrail("p0", "signal_aggregator_engine", "p0_governance")
emit_replay_key("p0", "signal_aggregator_engine")
emit_determinism_digest("p0", "signal_aggregator_engine")
_emit_writes_via_uwg("p2", "signal_aggregator_engine", "uwg_write")
_emit_blocks_direct_write("p2", "signal_aggregator_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "signal_aggregator_engine", "tool_invocation")
_emit_captures_execution_output("p2", "signal_aggregator_engine", "exec_output")
_emit_dispatches_agent("p3", "signal_aggregator_engine", "agent_dispatch")
_emit_dispatches_execution_plan("p3", "signal_aggregator_engine", "exec_plan")
_emit_routes_to_agent("p3", "signal_aggregator_engine", "target_agent")
_emit_checks_agent_registry("p3", "signal_aggregator_engine", "agent_registry")
_emit_validates_agent_capability("p3", "signal_aggregator_engine", "capability")
_emit_verifies_policy("p3", "signal_aggregator_engine", "policy_check")
_emit_verifies_boundary("p3", "signal_aggregator_engine", "boundary_check")
_emit_agent_executes_agent("p3", "signal_aggregator_engine", "sub_agent")

logger = logging.getLogger(__name__)


# =============================================================================
# Signal Aggregator Types
# =============================================================================


@dataclass(frozen=True)
class PreferenceGrade:
    """Individual preference grade from BUS P.

    Attributes
    ----------
    metric_name:
        Name of the qualitative metric (e.g., "task_completion", "groundedness").
    score:
        Numeric score (typically 0.0 to 1.0).
    confidence:
        Confidence in the score (0.0 to 1.0).
    grader_id:
        Identifier of the grader that produced this score.
    """

    metric_name: str
    score: float
    confidence: float
    grader_id: str

    def __post_init__(self) -> None:
        if not self.metric_name:
            raise ValueError("metric_name must not be empty")
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(f"score must be in [0.0, 1.0], got {self.score}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be in [0.0, 1.0], got {self.confidence}")

    def to_dict(self) -> dict[str, object]:
        return {
            "confidence": self.confidence,
            "grader_id": self.grader_id,
            "metric_name": self.metric_name,
            "score": self.score,
        }


@dataclass(frozen=True)
class TelemetryMetric:
    """Individual telemetry metric from BUS T.

    Attributes
    ----------
    metric_name:
        Name of the quantitative metric (e.g., "latency_ms", "token_count").
    value:
        Numeric value of the metric.
    unit:
        Unit of measurement.
    source:
        Source system that emitted this metric.
    """

    metric_name: str
    value: float
    unit: str
    source: str

    def __post_init__(self) -> None:
        if not self.metric_name:
            raise ValueError("metric_name must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "metric_name": self.metric_name,
            "source": self.source,
            "unit": self.unit,
            "value": self.value,
        }


@dataclass(frozen=True)
class AggregatedSignalBundle:
    """Aggregated signal bundle — output of Component E.

    Contains unified evaluation signals per Evaluation Spine spec.

    Attributes
    ----------
    bundle_id:
        Deterministic SHA-256 ID for this bundle.
    trace_id:
        Source execution trace identifier.
    score_bundle:
        Map of metric names to aggregated scores.
    decisiveness_tag:
        Classification of decisiveness (HIGH_CONFIDENCE, LOW_CONFIDENCE, CONFLICTING).
    drift_flags:
        List of drift indicators detected.
    confidence:
        Overall confidence score (0.0 to 1.0).
    variance:
        Variance metric for score stability.
    severity_class:
        Severity classification (INFO, WARNING, CRITICAL).
    source_digest:
        SHA-256 of source BUS P and BUS T data.
    timestamp_utc:
        Unix timestamp provided by caller.
    """

    bundle_id: str
    trace_id: str
    score_bundle: dict[str, float]
    decisiveness_tag: Literal["HIGH_CONFIDENCE", "LOW_CONFIDENCE", "CONFLICTING", "INSUFFICIENT_DATA"]
    drift_flags: tuple[str, ...]
    confidence: float
    variance: float
    severity_class: Literal["INFO", "WARNING", "CRITICAL"]
    source_digest: str
    timestamp_utc: int

    def __post_init__(self) -> None:
        if not self.bundle_id:
            raise ValueError("bundle_id must not be empty")
        if not self.trace_id:
            raise ValueError("trace_id must not be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be in [0.0, 1.0], got {self.confidence}")
        if self.variance < 0.0:
            raise ValueError(f"variance must be non-negative, got {self.variance}")

    def to_dict(self) -> dict[str, object]:
        return {
            "bundle_id": self.bundle_id,
            "confidence": self.confidence,
            "decisiveness_tag": self.decisiveness_tag,
            "drift_flags": list(self.drift_flags),
            "score_bundle": self.score_bundle,
            "severity_class": self.severity_class,
            "source_digest": self.source_digest,
            "timestamp_utc": self.timestamp_utc,
            "trace_id": self.trace_id,
            "variance": self.variance,
        }

    def to_json(self) -> str:
        return deterministic_json(self.to_dict())

    def stable_hash(self) -> str:
        return stable_sha256_json(self.to_dict())


# =============================================================================
# SignalAggregatorEngine
# =============================================================================


class SignalAggregatorEngine:
    """Engine for aggregating BUS P and BUS T into unified evaluation signals.

    Implements Evaluation Spine Component E per documentation:
        - Score bundling
        - Decisiveness tags
        - Drift flags
        - Confidence/variance metrics
        - Severity classification

    Deterministic: Same inputs always produce same output hash.
    Fail-closed: Insufficient or conflicting data produces LOW_CONFIDENCE.

    Attributes
    ----------
    min_confidence_threshold:
        Minimum confidence to tag as HIGH_CONFIDENCE.
    max_variance_threshold:
        Maximum variance before flagging as unstable.
    """

    def __init__(
        self,
        min_confidence_threshold: float = 0.7,
        max_variance_threshold: float = 0.3,
    ) -> None:
        self.min_confidence_threshold = min_confidence_threshold
        self.max_variance_threshold = max_variance_threshold

    def aggregate_signals(
        self,
        trace_id: str,
        preferences: list[PreferenceGrade],
        telemetry: list[TelemetryMetric],
        timestamp_utc: int,
    ) -> AggregatedSignalBundle:
        """Aggregate BUS P (preferences) and BUS T (telemetry) into unified signals.

        Parameters
        ----------
        trace_id:
            Source execution trace identifier.
        preferences:
            List of qualitative preference grades from BUS P.
        telemetry:
            List of quantitative telemetry metrics from BUS T.
        timestamp_utc:
            Unix timestamp provided by caller (no wall-clock reads).

        Returns
        -------
        AggregatedSignalBundle
            Deterministic aggregated signal bundle.
        """
        _emit_records_execution_trace("signal_aggregator_engine", "aggregate_start", trace_id)

        # ---------------------------------------------------------------------
        # Build score bundle from preferences
        # ---------------------------------------------------------------------
        score_bundle = self._build_score_bundle(preferences)

        # ---------------------------------------------------------------------
        # Calculate confidence and variance
        # ---------------------------------------------------------------------
        confidence = self._calculate_confidence(preferences)
        variance = self._calculate_variance(preferences)

        # ---------------------------------------------------------------------
        # Determine decisiveness tag
        # ---------------------------------------------------------------------
        decisiveness_tag = self._determine_decisiveness(
            preferences,
            confidence,
            variance,
        )

        # ---------------------------------------------------------------------
        # Detect drift flags
        # ---------------------------------------------------------------------
        drift_flags = self._detect_drift_flags(
            preferences,
            telemetry,
            variance,
        )

        # ---------------------------------------------------------------------
        # Classify severity
        # ---------------------------------------------------------------------
        severity_class = self._classify_severity(
            confidence,
            variance,
            drift_flags,
        )

        # ---------------------------------------------------------------------
        # Compute source digest
        # ---------------------------------------------------------------------
        source_digest = stable_sha256_json(
            {
                "preferences": [p.to_dict() for p in preferences],
                "telemetry": [t.to_dict() for t in telemetry],
            },
        )

        # ---------------------------------------------------------------------
        # Build final bundle
        # ---------------------------------------------------------------------
        bundle = AggregatedSignalBundle(
            bundle_id=stable_sha256_json(
                {
                    "trace_id": trace_id,
                    "source_digest": source_digest,
                    "timestamp_utc": timestamp_utc,
                },
            ),
            trace_id=trace_id,
            score_bundle=score_bundle,
            decisiveness_tag=decisiveness_tag,
            drift_flags=tuple(sorted(drift_flags)),
            confidence=confidence,
            variance=variance,
            severity_class=severity_class,
            source_digest=source_digest,
            timestamp_utc=timestamp_utc,
        )

        _emit_records_execution_trace(
            "signal_aggregator_engine",
            "aggregate_complete",
            f"bundle_id={bundle.bundle_id}",
        )

        logger.info(
            "Signal aggregation complete: trace_id=%s, bundle_id=%s, decisiveness=%s, severity=%s",
            trace_id,
            bundle.bundle_id,
            decisiveness_tag,
            severity_class,
        )

        return bundle

    def _build_score_bundle(
        self,
        preferences: list[PreferenceGrade],
    ) -> dict[str, float]:
        """Build aggregated score bundle from preferences.

        Groups preferences by metric_name and computes mean score.
        """
        if not preferences:
            return {}

        scores_by_metric: dict[str, list[float]] = {}

        for pref in preferences:
            if pref.metric_name not in scores_by_metric:
                scores_by_metric[pref.metric_name] = []
            scores_by_metric[pref.metric_name].append(pref.score)

        # Compute mean for each metric
        score_bundle = {metric: sum(scores) / len(scores) for metric, scores in scores_by_metric.items()}

        return score_bundle

    def _calculate_confidence(
        self,
        preferences: list[PreferenceGrade],
    ) -> float:
        """Calculate overall confidence from preference confidences.

        Uses mean confidence weighted by score variance.
        """
        if not preferences:
            return 0.0

        # Mean of individual confidences
        mean_confidence = sum(p.confidence for p in preferences) / len(preferences)

        # Penalize if preferences disagree
        if len(preferences) > 1:
            scores = [p.score for p in preferences]
            score_variance = self._compute_variance(scores)
            # Reduce confidence by variance amount
            mean_confidence = max(0.0, mean_confidence - score_variance)

        return round(mean_confidence, 6)  # Deterministic rounding

    def _calculate_variance(
        self,
        preferences: list[PreferenceGrade],
    ) -> float:
        """Calculate variance metric for score stability."""
        if len(preferences) < 2:
            return 0.0

        scores = [p.score for p in preferences]
        return self._compute_variance(scores)

    def _compute_variance(self, values: list[float]) -> float:
        """Compute population variance of a list of values."""
        if len(values) < 2:
            return 0.0

        mean = sum(values) / len(values)
        squared_diffs = [(x - mean) ** 2 for x in values]
        variance = sum(squared_diffs) / len(squared_diffs)

        return round(variance, 6)  # Deterministic rounding

    def _determine_decisiveness(
        self,
        preferences: list[PreferenceGrade],
        confidence: float,
        variance: float,
    ) -> Literal["HIGH_CONFIDENCE", "LOW_CONFIDENCE", "CONFLICTING", "INSUFFICIENT_DATA"]:
        """Determine decisiveness tag based on data quality.

        HIGH_CONFIDENCE: High confidence, low variance, consistent grades
        LOW_CONFIDENCE: Low confidence or high variance
        CONFLICTING: Significant disagreement between graders
        INSUFFICIENT_DATA: Not enough preferences to make determination
        """
        if len(preferences) < 1:
            return "INSUFFICIENT_DATA"

        if len(preferences) >= 2:
            # Check for conflicting grades
            scores = [p.score for p in preferences]
            score_range = max(scores) - min(scores)
            if score_range > 0.5:  # Significant disagreement
                return "CONFLICTING"

        if confidence >= self.min_confidence_threshold and variance <= self.max_variance_threshold:
            return "HIGH_CONFIDENCE"

        return "LOW_CONFIDENCE"

    def _detect_drift_flags(
        self,
        preferences: list[PreferenceGrade],
        telemetry: list[TelemetryMetric],
        variance: float,
    ) -> list[str]:
        """Detect drift indicators from preferences and telemetry.

        Returns list of drift flag strings.
        """
        drift_flags: list[str] = []

        # Flag high variance
        if variance > self.max_variance_threshold:
            drift_flags.append(f"HIGH_VARIANCE:{variance:.4f}")

        # Flag confidence degradation
        if preferences:
            confidences = [p.confidence for p in preferences]
            mean_confidence = sum(confidences) / len(confidences)
            if mean_confidence < 0.5:
                drift_flags.append(f"LOW_CONFIDENCE:{mean_confidence:.4f}")

        # Flag missing expected telemetry
        metric_names = {t.metric_name for t in telemetry}
        expected_telemetry = {"latency_ms", "token_count"}
        missing = expected_telemetry - metric_names
        if missing:
            drift_flags.append(f"MISSING_TELEMETRY:{','.join(sorted(missing))}")

        return drift_flags

    def _classify_severity(
        self,
        confidence: float,
        variance: float,
        drift_flags: list[str],
    ) -> Literal["INFO", "WARNING", "CRITICAL"]:
        """Classify severity based on signal quality indicators.

        CRITICAL: Very low confidence or multiple drift flags
        WARNING: Moderate issues detected
        INFO: Clean signals
        """
        # Critical conditions
        if confidence < 0.3 or len(drift_flags) >= 3:
            return "CRITICAL"

        # Warning conditions
        if confidence < 0.6 or variance > self.max_variance_threshold or len(drift_flags) >= 1:
            return "WARNING"

        return "INFO"


__all__ = [
    "AggregatedSignalBundle",
    "PreferenceGrade",
    "SignalAggregatorEngine",
    "TelemetryMetric",
]
