"""Pattern Analysis Engine - Phase 8.

Analyzes healing outcomes and drift signals to generate deterministic findings.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from system_learning.types.healing_outcome_learning_types import (
    HealingOutcomeAggregate,
    HealingOutcomeAggregateKey,
    HealingOutcomeAggregateSnapshot,
)
from system_learning.types.pattern_analysis_types import (
    PatternFinding,
    PatternFindingKey,
    PatternFindingReport,
    PatternSourceIds,
)


@dataclass(frozen=True, slots=True)
class PatternAnalysisConfig:
    """Configuration for pattern analysis thresholds."""

    # Underperforming healer thresholds
    success_rate_threshold_low: float = 0.5
    min_observations: int = 20

    # Flapping healer thresholds
    flapping_variance_epsilon: float = 0.1

    # Drift and detection thresholds
    drift_trigger_threshold: float = 0.7
    spike_trigger_threshold: float = 0.8


class PatternAnalysisEngine:
    """Engine for analyzing patterns in healing outcomes and drift signals."""

    def __init__(self, config: PatternAnalysisConfig | None = None) -> None:
        self.config = config or PatternAnalysisConfig()

    def analyze(
        self,
        *,
        healing_snapshot_bytes: bytes,
        detection_signal_bytes: bytes | None,
        drift_snapshot_bytes: bytes | None,
        now_utc: int,
    ) -> PatternFindingReport:
        """Analyze patterns and generate findings report.

        Args:
            healing_snapshot_bytes: Serialized healing outcome snapshot
            detection_signal_bytes: Serialized detection signal (optional)
            drift_snapshot_bytes: Serialized drift snapshot (optional)
            now_utc: Current time for deterministic analysis

        Returns:
            PatternFindingReport with deterministic findings
        """
        # Parse healing snapshot
        healing_snapshot = self._parse_healing_snapshot(healing_snapshot_bytes)

        # Parse optional inputs
        detection_data = (
            self._parse_detection_signal(detection_signal_bytes) if detection_signal_bytes else None
        )
        drift_data = self._parse_drift_snapshot(drift_snapshot_bytes) if drift_snapshot_bytes else None

        # Generate source IDs
        source_ids = PatternSourceIds(
            healing_snapshot_version=healing_snapshot.version_id,
            detection_signal_version=detection_data.get("version") if detection_data else None,
            drift_snapshot_version=drift_data.get("version") if drift_data else None,
        )

        # Collect findings
        findings = []

        # Analyze healing outcomes
        healing_findings = self._analyze_healing_outcomes(healing_snapshot)
        findings.extend(healing_findings)

        # Analyze drift if present
        if drift_data:
            drift_findings = self._analyze_drift(drift_data)
            findings.extend(drift_findings)

        # Analyze detection signals if present
        if detection_data:
            detection_findings = self._analyze_detection_signals(detection_data)
            findings.extend(detection_findings)

        # Sort findings deterministically
        findings.sort(key=lambda f: (f.key.component, f.key.dimension, f.key.label))

        return PatternFindingReport(
            source_ids=source_ids,
            findings=tuple(findings),
        )

    def _parse_healing_snapshot(self, bytes_data: bytes) -> HealingOutcomeAggregateSnapshot:
        """Parse healing snapshot from bytes."""
        try:
            data = json.loads(bytes_data.decode("utf-8"))

            # Parse aggregates
            aggregates = []
            for agg_data in data.get("aggregates", []):
                key_data = agg_data["key"]
                aggregate_data = agg_data["aggregate"]

                key = HealingOutcomeAggregateKey(
                    healer_name=key_data["healer_name"],
                    tier=key_data["tier"],
                    failure_type=key_data["failure_type"],
                )

                aggregate = HealingOutcomeAggregate(
                    success_count=aggregate_data["success_count"],
                    failure_count=aggregate_data["failure_count"],
                    total_count=aggregate_data["total_count"],
                )

                aggregates.append((key, aggregate))

            # Sort aggregates deterministically
            aggregates.sort(key=lambda pair: (pair[0].healer_name, pair[0].tier, pair[0].failure_type))

            return HealingOutcomeAggregateSnapshot(
                version_id=data["version_id"], created_utc=data["created_utc"], aggregates=tuple(aggregates)
            )
        except (json.JSONDecodeError, UnicodeDecodeError, KeyError, ValueError) as e:
            raise ValueError(f"Invalid healing snapshot bytes: {e}")

    def _parse_detection_signal(self, bytes_data: bytes) -> dict[str, Any] | None:
        """Parse detection signal from bytes."""
        try:
            return json.loads(bytes_data.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

    def _parse_drift_snapshot(self, bytes_data: bytes) -> dict[str, Any] | None:
        """Parse drift snapshot from bytes."""
        try:
            return json.loads(bytes_data.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

    def _analyze_healing_outcomes(self, snapshot: HealingOutcomeAggregateSnapshot) -> list[PatternFinding]:
        """Analyze healing outcomes for patterns."""
        findings = []

        for key, aggregate in snapshot.aggregates:
            # Check underperforming healer tier
            if (
                aggregate.success_rate < self.config.success_rate_threshold_low
                and aggregate.total_count >= self.config.min_observations
            ):
                finding = PatternFinding(
                    key=PatternFindingKey(
                        component=key.healer_name,
                        dimension="performance",
                        label="UNDERPERFORMING_HEALER_TIER",
                    ),
                    severity=round(1.0 - aggregate.success_rate, 6),
                    evidence=(
                        f"success_rate_{aggregate.success_rate:.6f}",
                        f"threshold_{self.config.success_rate_threshold_low:.6f}",
                        f"sample_size_{aggregate.total_count}",
                    ),
                    metrics=(
                        ("success_rate", aggregate.success_rate),
                        ("sample_size", aggregate.total_count),
                        ("error_rate", 1.0 - aggregate.success_rate),
                    ),
                )
                findings.append(finding)

            # Check for flapping (if we have bucket data)
            if hasattr(aggregate, "bucket_success_rates") and aggregate.bucket_success_rates:
                variance = self._calculate_variance(aggregate.bucket_success_rates)
                if variance > self.config.flapping_variance_epsilon:
                    finding = PatternFinding(
                        key=PatternFindingKey(
                            component=key.healer_name,
                            dimension="stability",
                            label="FLAPPING_HEALER_TIER",
                        ),
                        severity=round(variance, 6),
                        evidence=(
                            f"variance_{variance:.6f}",
                            f"threshold_{self.config.flapping_variance_epsilon:.6f}",
                            f"bucket_count_{len(aggregate.bucket_success_rates)}",
                        ),
                        metrics=(
                            ("variance", variance),
                            ("bucket_count", len(aggregate.bucket_success_rates)),
                            ("success_rate", aggregate.success_rate),
                        ),
                    )
                    findings.append(finding)

        return findings

    def _analyze_drift(self, drift_data: dict[str, Any]) -> list[PatternFinding]:
        """Analyze drift data for patterns."""
        findings = []

        # Look for high drift scores
        drift_scores = drift_data.get("drift_scores", [])
        for score_data in drift_scores:
            if isinstance(score_data, dict):
                component = score_data.get("component", "unknown")
                drift_score = score_data.get("score", 0.0)

                if drift_score >= self.config.drift_trigger_threshold:
                    finding = PatternFinding(
                        key=PatternFindingKey(
                            component=component,
                            dimension="drift",
                            label="ROUTING_DRIFT_HIGH",
                        ),
                        severity=round(drift_score, 6),
                        evidence=(
                            f"drift_score_{drift_score:.6f}",
                            f"threshold_{self.config.drift_trigger_threshold:.6f}",
                        ),
                        metrics=(
                            ("drift_score", drift_score),
                            ("threshold", self.config.drift_trigger_threshold),
                        ),
                    )
                    findings.append(finding)

        return findings

    def _analyze_detection_signals(self, detection_data: dict[str, Any]) -> list[PatternFinding]:
        """Analyze detection signals for patterns."""
        findings = []

        # Look for spike in severity
        signals = detection_data.get("signals", [])
        for signal in signals:
            if isinstance(signal, dict):
                component = signal.get("component", "unknown")
                severity = signal.get("severity", 0.0)

                if severity >= self.config.spike_trigger_threshold:
                    finding = PatternFinding(
                        key=PatternFindingKey(
                            component=component,
                            dimension="detection",
                            label="DETECTION_SIGNAL_SPIKE",
                        ),
                        severity=round(severity, 6),
                        evidence=(
                            f"severity_{severity:.6f}",
                            f"threshold_{self.config.spike_trigger_threshold:.6f}",
                        ),
                        metrics=(
                            ("severity", severity),
                            ("threshold", self.config.spike_trigger_threshold),
                        ),
                    )
                    findings.append(finding)

        return findings

    def _calculate_variance(self, values: list[float]) -> float:
        """Calculate variance of a list of values."""
        if not values:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance
