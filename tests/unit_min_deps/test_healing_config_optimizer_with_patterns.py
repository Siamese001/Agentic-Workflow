"""Tests for Healing Config Optimizer with Pattern Findings - Phase 8."""

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

from system_learning.engines.healing_config_optimizer import (
    HealingConfigOptimizer,
)
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


class TestHealingConfigOptimizerWithPatterns:
    """Test suite for Healing Config Optimizer with pattern findings."""

    def test_bounded_delta_applied(self):
        """Test that pattern findings trigger bounded adjustments."""
        optimizer = HealingConfigOptimizer(
            escalation_delta=0.1,
            max_delta=0.2,  # Small max delta for testing
            max_threshold=THRESHOLD,
        )

        # Create snapshot
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

        # Create pattern finding with high severity
        pattern_report = PatternFindingReport(
            source_ids=PatternSourceIds(healing_snapshot_version="test_v1"),
            findings=(
                PatternFinding(
                    key=PatternFindingKey(
                        component="test_healer", dimension="performance", label="UNDERPERFORMING_HEALER_TIER"
                    ),
                    severity=1.0,  # High severity
                    evidence=("success_rate_0.300000", "threshold_0.500000"),
                    metrics=(
                        ("success_rate", 0.3),
                        ("sample_size", 100),
                    ),
                ),
            ),
        )

        # Get proposal with patterns
        proposal = optimizer.propose_threshold_adjustments_with_patterns(snapshot, pattern_report)

        # Check that adjustment is bounded
        assert len(proposal.adjustments) == 1
        adj = proposal.adjustments[0]

        # Current threshold for LOCAL_AGENT is 0.5
        assert adj.current_threshold == 0.5
        # Proposed threshold should be current + min(escalation_delta * severity, max_delta)
        # = 0.5 + min(0.1 * 1.0, 0.2) = 0.5 + 0.1 = 0.6
        assert adj.proposed_threshold == 0.6
        assert adj.proposed_threshold - adj.current_threshold <= optimizer._max_delta
        assert adj.proposed_threshold <= optimizer._max_threshold

        # Check reason includes pattern finding
        assert "Pattern finding: UNDERPERFORMING_HEALER_TIER" in adj.reason
        assert "severity=1.000" in adj.reason

    def test_multiple_findings_deterministic_application_order(self):
        """Test that multiple findings are applied in deterministic order."""
        optimizer = HealingConfigOptimizer(escalation_delta=0.1, max_delta=0.3, max_threshold=THRESHOLD)

        # Create snapshot
        aggregates = [
            (
                HealingOutcomeAggregateKey(
                    healer_name="healer_a", tier="LOCAL_AGENT", failure_type="timeout"
                ),
                HealingOutcomeAggregate(success_count=80, failure_count=20, total_count=100),
            )
        ]

        snapshot = HealingOutcomeAggregateSnapshot(
            version_id="test_v1", created_utc=1000, aggregates=tuple(aggregates)
        )

        # Create multiple findings in reverse order to test sorting
        pattern_report = PatternFindingReport(
            source_ids=PatternSourceIds(healing_snapshot_version="test_v1"),
            findings=(
                PatternFinding(
                    key=PatternFindingKey(
                        component="healer_z", dimension="performance", label="UNDERPERFORMING_HEALER_TIER"
                    ),
                    severity=0.5,
                    evidence=("success_rate_0.300000",),
                    metrics=(("success_rate", 0.3),),
                ),
                PatternFinding(
                    key=PatternFindingKey(
                        component="healer_a", dimension="performance", label="UNDERPERFORMING_HEALER_TIER"
                    ),
                    severity=0.8,
                    evidence=("success_rate_0.200000",),
                    metrics=(("success_rate", 0.2),),
                ),
                PatternFinding(
                    key=PatternFindingKey(
                        component="healer_m", dimension="performance", label="UNDERPERFORMING_HEALER_TIER"
                    ),
                    severity=0.6,
                    evidence=("success_rate_0.400000",),
                    metrics=(("success_rate", 0.4),),
                ),
            ),
        )

        # Get proposal twice
        proposal1 = optimizer.propose_threshold_adjustments_with_patterns(snapshot, pattern_report)

        proposal2 = optimizer.propose_threshold_adjustments_with_patterns(snapshot, pattern_report)

        # Check deterministic ordering (should be sorted by component name)
        assert len(proposal1.adjustments) == 3
        assert proposal1.adjustments[0].healer_name == "healer"  # From "healer_a" split
        assert proposal1.adjustments[1].healer_name == "healer"  # From "healer_m" split
        assert proposal1.adjustments[2].healer_name == "healer"  # From "healer_z" split

        # Check identical proposals across runs
        assert proposal1.canonical_bytes() == proposal2.canonical_bytes()
        assert proposal1.content_hash() == proposal2.content_hash()

    def test_routing_drift_tightens_thresholds(self):
        """Test that ROUTING_DRIFT_HIGH finding tightens thresholds."""
        optimizer = HealingConfigOptimizer(escalation_delta=0.1, max_delta=0.2, max_threshold=THRESHOLD)

        # Create snapshot
        aggregates = [
            (
                HealingOutcomeAggregateKey(
                    healer_name="router_agent", tier="LOCAL_AGENT", failure_type="timeout"
                ),
                HealingOutcomeAggregate(success_count=90, failure_count=10, total_count=100),
            )
        ]

        snapshot = HealingOutcomeAggregateSnapshot(
            version_id="test_v1", created_utc=1000, aggregates=tuple(aggregates)
        )

        # Create drift finding
        pattern_report = PatternFindingReport(
            source_ids=PatternSourceIds(healing_snapshot_version="test_v1"),
            findings=(
                PatternFinding(
                    key=PatternFindingKey(
                        component="router_agent", dimension="drift", label="ROUTING_DRIFT_HIGH"
                    ),
                    severity=0.8,
                    evidence=("drift_score_0.800000",),
                    metrics=(("drift_score", 0.8),),
                ),
            ),
        )

        # Get proposal
        proposal = optimizer.propose_threshold_adjustments_with_patterns(snapshot, pattern_report)

        # Check that threshold is tightened (decreased)
        assert len(proposal.adjustments) == 1
        adj = proposal.adjustments[0]

        # Current threshold for LOCAL_AGENT is 0.5
        assert adj.current_threshold == 0.5
        # Should decrease by escalation_delta * severity * 0.5
        # = 0.5 - (0.1 * 0.8 * 0.5) = 0.5 - 0.04 = 0.46 (allowing for floating point precision)
        assert abs(adj.proposed_threshold - 0.46) < 1e-10
        assert adj.failure_type == "drift_based"
        assert "ROUTING_DRIFT_HIGH" in adj.reason

    def test_max_delta_clamping(self):
        """Test that adjustments are clamped to max_delta per healer."""
        optimizer = HealingConfigOptimizer(
            escalation_delta=0.2,  # Large delta
            max_delta=0.1,  # Small max delta
            max_threshold=THRESHOLD,
        )

        # Create snapshot
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

        # Create two findings that would exceed max_delta
        pattern_report = PatternFindingReport(
            source_ids=PatternSourceIds(healing_snapshot_version="test_v1"),
            findings=(
                PatternFinding(
                    key=PatternFindingKey(
                        component="test_healer", dimension="performance", label="UNDERPERFORMING_HEALER_TIER"
                    ),
                    severity=1.0,  # Would add 0.2
                    evidence=("success_rate_0.300000",),
                    metrics=(("success_rate", 0.3),),
                ),
                PatternFinding(
                    key=PatternFindingKey(
                        component="test_healer", dimension="drift", label="ROUTING_DRIFT_HIGH"
                    ),
                    severity=1.0,  # Would subtract 0.1
                    evidence=("drift_score_0.800000",),
                    metrics=(("drift_score", 0.8),),
                ),
            ),
        )

        # Get proposal
        proposal = optimizer.propose_threshold_adjustments_with_patterns(snapshot, pattern_report)

        # Check that total delta is clamped to max_delta
        assert len(proposal.adjustments) == 2

        # Calculate total delta
        total_delta = sum(adj.proposed_threshold - adj.current_threshold for adj in proposal.adjustments)

        # Should be clamped to max_delta = 0.1
        assert abs(total_delta) <= optimizer._max_delta

        # Check that scaling is mentioned in reason
        for adj in proposal.adjustments:
            if "scaled to max_delta" in adj.reason:
                assert "0.100000" in adj.reason
