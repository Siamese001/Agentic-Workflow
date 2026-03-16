"""Tests for HealingConfigOptimizer - Phase 6 functionality.

Tests threshold adjustment proposals and deterministic behavior.
"""

from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_healing_config_optimizer")
_emit_applies_guardrail("p0", "test_healing_config_optimizer", "p0_governance")
_emit_reads_policy_state("p0", "test_healing_config_optimizer", "policy_binding")
_emit_snapshots_state("p0", "test_healing_config_optimizer", "state_snapshot")
emit_replay_key("p0", "test_healing_config_optimizer")
emit_determinism_digest("p0", "test_healing_config_optimizer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
    ThresholdAdjustment,
    ThresholdAdjustmentProposal,
)
from system_learning.types.healing_outcome_intake_types import HealingOutcomeIntakeRecord
from system_learning.types.healing_outcome_learning_types import (
    HealingOutcomeAggregate,
    HealingOutcomeAggregateKey,
    HealingOutcomeAggregateSnapshot,
)
from system_learning.types.healing_outcome_types import HealingOutcomeStats


class TestHealingConfigOptimizer:
    """Test suite for HealingConfigOptimizer."""

    def test_threshold_proposal_deterministic(self):
        """Test that proposals are deterministic given same input."""
        optimizer = HealingConfigOptimizer(
            min_sample_size=10, low_success_rate_threshold=THRESHOLD, escalation_delta=0.1, max_threshold=THRESHOLD
        )

        # Create test snapshot
        aggregates = [
            (
                HealingOutcomeAggregateKey("healer1", "LOCAL_AGENT", "failure1"),
                HealingOutcomeAggregate(success_count=3, failure_count=7, total_count=10),
            ),
            (
                HealingOutcomeAggregateKey("healer2", "REMOTE_AGENT", "failure2"),
                HealingOutcomeAggregate(success_count=8, failure_count=2, total_count=10),
            ),
        ]

        snapshot = HealingOutcomeAggregateSnapshot(
            version_id="test123", created_utc=2000, aggregates=tuple(aggregates)
        )

        # Generate proposals twice
        proposal1 = optimizer.propose_threshold_adjustments(snapshot)
        proposal2 = optimizer.propose_threshold_adjustments(snapshot)

        # Should be identical
        assert proposal1.content_hash() == proposal2.content_hash()
        assert len(proposal1.adjustments) == len(proposal2.adjustments)

        # Only healer1 should have adjustment (30% success < 60% threshold)
        assert len(proposal1.adjustments) == 1
        adjustment = proposal1.adjustments[0]
        assert adjustment.healer_name == "healer1"
        assert adjustment.tier == "LOCAL_AGENT"
        assert adjustment.failure_type == "failure1"
        assert adjustment.current_threshold == 0.5  # Default for LOCAL_AGENT
        assert adjustment.proposed_threshold == 0.6  # 0.5 + 0.1

    def test_no_direct_config_mutation(self):
        """Test that optimizer doesn't directly mutate any config."""
        optimizer = HealingConfigOptimizer()

        # Create empty snapshot
        snapshot = HealingOutcomeAggregateSnapshot(version_id="empty", created_utc=2000, aggregates=())

        # Should not raise any errors and produce no adjustments
        proposal = optimizer.propose_threshold_adjustments(snapshot)
        assert len(proposal.adjustments) == 0
        assert proposal.snapshot_version_id == "empty"
        assert proposal.created_utc == 2000

    def test_minimum_sample_size_enforced(self):
        """Test that proposals require minimum sample size."""
        optimizer = HealingConfigOptimizer(min_sample_size=50)

        # Create snapshot with insufficient samples
        aggregates = [
            (
                HealingOutcomeAggregateKey("healer1", "LOCAL_AGENT", "failure1"),
                HealingOutcomeAggregate(success_count=1, failure_count=9, total_count=10),
            ),
        ]

        snapshot = HealingOutcomeAggregateSnapshot(
            version_id="test", created_utc=2000, aggregates=tuple(aggregates)
        )

        # Should not propose adjustment due to insufficient sample size
        proposal = optimizer.propose_threshold_adjustments(snapshot)
        assert len(proposal.adjustments) == 0

    def test_max_threshold_capped(self):
        """Test that proposed thresholds are capped at max_threshold."""
        optimizer = HealingConfigOptimizer(
            min_sample_size=10,
            low_success_rate_threshold=THRESHOLD,
            escalation_delta=1.5,  # Large delta
            max_threshold=THRESHOLD,  # Low max
        )

        # Create snapshot with low success rate
        aggregates = [
            (
                HealingOutcomeAggregateKey("healer1", "LOCAL_AGENT", "failure1"),
                HealingOutcomeAggregate(success_count=1, failure_count=9, total_count=10),
            ),
        ]

        snapshot = HealingOutcomeAggregateSnapshot(
            version_id="test", created_utc=2000, aggregates=tuple(aggregates)
        )

        proposal = optimizer.propose_threshold_adjustments(snapshot)
        assert len(proposal.adjustments) == 1

        adjustment = proposal.adjustments[0]
        # Current 0.5 + 1.5 = 2.0, but capped at 1.0
        assert adjustment.proposed_threshold == 1.0

    def test_create_snapshot_from_intake(self):
        """Test creating aggregate snapshot from intake record."""
        optimizer = HealingConfigOptimizer()

        # Create mock intake record
        stats = (
            HealingOutcomeStats.from_counts("healer1", "LOCAL_AGENT", "failure1", 7, 3),
            HealingOutcomeStats.from_counts("healer2", "REMOTE_AGENT", "failure2", 5, 5),
        )

        intake_record = HealingOutcomeIntakeRecord(
            schema_version=1,
            created_utc=1000,
            window_size=100,
            snapshot=stats,
            proposal=None,  # type: ignore
            source="test",
        )

        # Create snapshot
        snapshot = optimizer.create_snapshot_from_intake(intake_record, created_utc=2000)

        assert snapshot.created_utc == 2000
        assert len(snapshot.aggregates) == 2
        assert snapshot.version_id != ""  # Should be computed hash

        # Check aggregates are sorted
        keys = [agg[0] for agg in snapshot.aggregates]
        assert keys[0].healer_name == "healer1"  # Should be sorted alphabetically
        assert keys[1].healer_name == "healer2"

        # Check content
        for key, aggregate in snapshot.aggregates:
            if key.healer_name == "healer1":
                assert aggregate.success_count == 7
                assert aggregate.failure_count == 3
                assert aggregate.total_count == 10
                assert aggregate.success_rate == 0.7
            elif key.healer_name == "healer2":
                assert aggregate.success_count == 5
                assert aggregate.failure_count == 5
                assert aggregate.total_count == 10
                assert aggregate.success_rate == 0.5

    def test_confidence_computation(self):
        """Test confidence score computation."""
        optimizer = HealingConfigOptimizer(min_sample_size=10)

        # Test with different sample sizes
        small_aggregate = HealingOutcomeAggregate(success_count=3, failure_count=7, total_count=10)
        large_aggregate = HealingOutcomeAggregate(success_count=30, failure_count=70, total_count=100)

        # Large sample should have higher confidence
        large_confidence = optimizer._compute_confidence(large_aggregate)
        small_confidence = optimizer._compute_confidence(small_aggregate)

        assert 0.0 <= small_confidence <= 1.0
        assert 0.0 <= large_confidence <= 1.0
        assert large_confidence > small_confidence

    def test_adjustment_canonical_bytes(self):
        """Test that adjustments have stable canonical bytes."""
        adjustment = ThresholdAdjustment(
            healer_name="healer1",
            tier="LOCAL_AGENT",
            failure_type="failure1",
            current_threshold=THRESHOLD,
            proposed_threshold=THRESHOLD,
            reason="Low success rate",
            confidence=0.8,
        )

        bytes1 = adjustment.canonical_bytes()
        bytes2 = adjustment.canonical_bytes()

        assert bytes1 == bytes2
        assert isinstance(bytes1, bytes)

        # Verify it's valid JSON
        import json

        data = json.loads(bytes1.decode("utf-8"))
        assert data["healer_name"] == "healer1"
        assert data["proposed_threshold"] == 0.6

    def test_proposal_canonical_bytes(self):
        """Test that proposals have stable canonical bytes."""
        adjustment = ThresholdAdjustment(
            healer_name="healer1",
            tier="LOCAL_AGENT",
            failure_type="failure1",
            current_threshold=THRESHOLD,
            proposed_threshold=THRESHOLD,
            reason="Low success rate",
            confidence=0.8,
        )

        proposal = ThresholdAdjustmentProposal(
            snapshot_version_id="test123", created_utc=2000, adjustments=(adjustment,)
        )

        bytes1 = proposal.canonical_bytes()
        bytes2 = proposal.canonical_bytes()

        assert bytes1 == bytes2
        assert isinstance(bytes1, bytes)

        # Verify it's valid JSON
        import json

        data = json.loads(bytes1.decode("utf-8"))
        assert data["snapshot_version_id"] == "test123"
        assert len(data["adjustments"]) == 1

    def test_optimizer_initialization_validation(self):
        """Test optimizer parameter validation."""
        # Valid initialization
        optimizer = HealingConfigOptimizer(
            min_sample_size=10, low_success_rate_threshold=THRESHOLD, escalation_delta=0.1, max_threshold=THRESHOLD
        )
        assert optimizer._min_sample_size == 10

        # Invalid min_sample_size
        with pytest.raises(ValueError, match="min_sample_size must be >= 1"):
            HealingConfigOptimizer(min_sample_size=0)

        # Invalid success rate threshold
        with pytest.raises(ValueError, match="low_success_rate_threshold must be in"):
            HealingConfigOptimizer(low_success_rate_threshold=THRESHOLD)

        # Invalid escalation delta
        with pytest.raises(ValueError, match="escalation_delta must be > 0"):
            HealingConfigOptimizer(escalation_delta=0)

        # Invalid max threshold
        with pytest.raises(ValueError, match="max_threshold must be > 0"):
            HealingConfigOptimizer(max_threshold=THRESHOLD)
