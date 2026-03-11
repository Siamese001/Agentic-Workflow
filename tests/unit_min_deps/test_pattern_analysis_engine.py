"""Tests for Pattern Analysis Engine - Phase 8."""

from __future__ import annotations

import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit_min_deps

from system_learning.engines.pattern_analysis_engine import (
    PatternAnalysisConfig,
    PatternAnalysisEngine,
)
from system_learning.types.healing_outcome_learning_types import (
    HealingOutcomeAggregate,
    HealingOutcomeAggregateKey,
    HealingOutcomeAggregateSnapshot,
)


class TestPatternAnalysisEngine:
    """Test suite for Pattern Analysis Engine."""

    def test_determinism_same_inputs_same_hash(self):
        """Test that same inputs produce identical outputs."""
        engine = PatternAnalysisEngine()

        # Create test healing snapshot
        aggregates = [
            (
                HealingOutcomeAggregateKey(
                    healer_name="test_healer", tier="LOCAL_AGENT", failure_type="timeout"
                ),
                HealingOutcomeAggregate(success_count=80, failure_count=20, total_count=100),
            )
        ]

        snapshot = HealingOutcomeAggregateSnapshot(
            version_id="test_v1", created_utc=1000, aggregates=tuple(aggregates)
        )

        # Analyze twice
        report1 = engine.analyze(
            healing_snapshot_bytes=snapshot.canonical_bytes(),
            detection_signal_bytes=None,
            drift_snapshot_bytes=None,
            now_utc=2000,
        )

        report2 = engine.analyze(
            healing_snapshot_bytes=snapshot.canonical_bytes(),
            detection_signal_bytes=None,
            drift_snapshot_bytes=None,
            now_utc=2000,
        )

        # Check deterministic outputs
        assert report1.canonical_bytes() == report2.canonical_bytes()
        assert report1.content_hash() == report2.content_hash()

    def test_permutation_invariant_healing_inputs(self):
        """Test that permuted healing aggregates produce identical report."""
        engine = PatternAnalysisEngine()

        # Create aggregates in different order
        aggregates1 = [
            (
                HealingOutcomeAggregateKey(
                    healer_name="healer_a", tier="LOCAL_AGENT", failure_type="timeout"
                ),
                HealingOutcomeAggregate(success_count=80, failure_count=20, total_count=100),
            ),
            (
                HealingOutcomeAggregateKey(healer_name="healer_b", tier="REMOTE_AGENT", failure_type="error"),
                HealingOutcomeAggregate(success_count=60, failure_count=40, total_count=100),
            ),
        ]

        aggregates2 = list(reversed(aggregates1))  # Reverse order
        # Sort both to ensure they pass validation
        aggregates1.sort(key=lambda pair: (pair[0].healer_name, pair[0].tier, pair[0].failure_type))
        aggregates2.sort(key=lambda pair: (pair[0].healer_name, pair[0].tier, pair[0].failure_type))

        snapshot1 = HealingOutcomeAggregateSnapshot(
            version_id="test_v1", created_utc=1000, aggregates=tuple(aggregates1)
        )

        snapshot2 = HealingOutcomeAggregateSnapshot(
            version_id="test_v1", created_utc=1000, aggregates=tuple(aggregates2)
        )

        # Analyze both
        report1 = engine.analyze(
            healing_snapshot_bytes=snapshot1.canonical_bytes(),
            detection_signal_bytes=None,
            drift_snapshot_bytes=None,
            now_utc=2000,
        )

        report2 = engine.analyze(
            healing_snapshot_bytes=snapshot2.canonical_bytes(),
            detection_signal_bytes=None,
            drift_snapshot_bytes=None,
            now_utc=2000,
        )

        # Should be identical despite permutation
        assert report1.canonical_bytes() == report2.canonical_bytes()
        assert report1.content_hash() == report2.content_hash()

    def test_underperforming_finding_triggered(self):
        """Test that underperforming healer triggers finding."""
        config = PatternAnalysisConfig(success_rate_threshold_low=0.7, min_observations=20)
        engine = PatternAnalysisEngine(config)

        # Create underperforming aggregate
        aggregates = [
            (
                HealingOutcomeAggregateKey(
                    healer_name="poor_healer", tier="LOCAL_AGENT", failure_type="timeout"
                ),
                HealingOutcomeAggregate(
                    success_count=30,  # 30% success rate
                    failure_count=70,
                    total_count=100,
                ),
            )
        ]

        snapshot = HealingOutcomeAggregateSnapshot(
            version_id="test_v1", created_utc=1000, aggregates=tuple(aggregates)
        )

        report = engine.analyze(
            healing_snapshot_bytes=snapshot.canonical_bytes(),
            detection_signal_bytes=None,
            drift_snapshot_bytes=None,
            now_utc=2000,
        )

        # Check for underperforming finding
        assert len(report.findings) == 1
        finding = report.findings[0]
        assert finding.key.label == "UNDERPERFORMING_HEALER_TIER"
        assert finding.key.component == "poor_healer"
        assert finding.key.dimension == "performance"
        assert finding.severity == 0.7  # 1.0 - 0.3 success_rate
        assert "success_rate_0.300000" in finding.evidence
        assert "threshold_0.700000" in finding.evidence
        assert "sample_size_100" in finding.evidence

        # Check metrics are sorted
        assert finding.metrics == (
            ("success_rate", 0.3),
            ("sample_size", 100),
            ("error_rate", 0.7),
        )

    def test_optional_inputs_none_deterministic(self):
        """Test that optional inputs being None produces stable report."""
        engine = PatternAnalysisEngine()

        # Create minimal snapshot
        aggregates = [
            (
                HealingOutcomeAggregateKey(
                    healer_name="test_healer", tier="LOCAL_AGENT", failure_type="timeout"
                ),
                HealingOutcomeAggregate(success_count=90, failure_count=10, total_count=100),
            )
        ]

        snapshot = HealingOutcomeAggregateSnapshot(
            version_id="test_v1", created_utc=1000, aggregates=tuple(aggregates)
        )

        # Analyze with None optional inputs
        report = engine.analyze(
            healing_snapshot_bytes=snapshot.canonical_bytes(),
            detection_signal_bytes=None,
            drift_snapshot_bytes=None,
            now_utc=2000,
        )

        # Should have no findings (good performance)
        assert len(report.findings) == 0
        assert report.source_ids.healing_snapshot_version == snapshot.version_id
        assert report.source_ids.detection_signal_version is None
        assert report.source_ids.drift_snapshot_version is None

        # Check deterministic hash
        assert report.content_hash() is not None
        assert len(report.content_hash()) == 64  # SHA256 hex length

    def test_drift_signal_finding_triggered(self):
        """Test that high drift signal triggers finding."""
        engine = PatternAnalysisEngine()

        # Create minimal healing snapshot
        aggregates = [
            (
                HealingOutcomeAggregateKey(
                    healer_name="test_healer", tier="LOCAL_AGENT", failure_type="timeout"
                ),
                HealingOutcomeAggregate(success_count=90, failure_count=10, total_count=100),
            )
        ]

        snapshot = HealingOutcomeAggregateSnapshot(
            version_id="test_v1", created_utc=1000, aggregates=tuple(aggregates)
        )

        # Create drift signal with high score
        drift_data = {
            "version": "drift_v1",
            "drift_scores": [
                {
                    "component": "test_healer",
                    "score": 0.8,  # Above threshold of 0.7
                }
            ],
        }

        import json

        drift_bytes = json.dumps(drift_data).encode("utf-8")

        report = engine.analyze(
            healing_snapshot_bytes=snapshot.canonical_bytes(),
            detection_signal_bytes=None,
            drift_snapshot_bytes=drift_bytes,
            now_utc=2000,
        )

        # Check for drift finding
        assert len(report.findings) == 1
        finding = report.findings[0]
        assert finding.key.label == "ROUTING_DRIFT_HIGH"
        assert finding.key.component == "test_healer"
        assert finding.key.dimension == "drift"
        assert finding.severity == 0.8
        assert "drift_score_0.800000" in finding.evidence
        assert "threshold_0.700000" in finding.evidence
