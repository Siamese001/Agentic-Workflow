"""Tests for reasoning_outcome_tracker — L6 Observability.

G1 Fix: Provides comprehensive test coverage for the ReasoningOutcomeTracker
which was previously completely untested.
"""
from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path

from agentic_core.L6_observability.telemetry.reasoning_outcome_tracker import (
    OutcomeAggregate,
    ReasoningOutcome,
    ReasoningOutcomeTracker,
)


class TestReasoningOutcome:
    """Test ReasoningOutcome dataclass."""

    def test_create_minimal(self):
        """Happy path: create with minimal required fields."""
        outcome = ReasoningOutcome.create(
            trace_id="trace-123",
            profile_hash="hash-abc",
            complexity_tier="moderate",
            path_id="cot",
            latency_ms=100.0,
            tokens_used=50,
        )
        assert outcome.trace_id == "trace-123"
        assert outcome.profile_hash == "hash-abc"
        assert outcome.complexity_tier == "moderate"
        assert outcome.path_id == "cot"
        assert outcome.latency_ms == 100.0
        assert outcome.tokens_used == 50
        assert outcome.timestamp > 0

    def test_create_full(self):
        """Happy path: create with all fields including optional."""
        outcome = ReasoningOutcome.create(
            trace_id="trace-456",
            profile_hash="hash-def",
            complexity_tier="complex",
            path_id="tot",
            latency_ms=500.0,
            tokens_used=200,
            quality_score=0.85,
            error_type=None,
            custom_field="value",
        )
        assert outcome.quality_score == 0.85
        assert outcome.error_type is None
        assert outcome.metadata == {"custom_field": "value"}

    def test_create_with_error(self):
        """Edge case: outcome with error information."""
        outcome = ReasoningOutcome.create(
            trace_id="trace-789",
            profile_hash=None,
            complexity_tier="simple",
            path_id="reflexion",
            latency_ms=50.0,
            tokens_used=25,
            error_type="TimeoutError",
            error_message="Request timed out",
        )
        assert outcome.error_type == "TimeoutError"
        assert outcome.metadata == {"error_message": "Request timed out"}


class TestReasoningOutcomeTracker:
    """Test ReasoningOutcomeTracker functionality."""

    def test_init_creates_directory(self):
        """Happy path: initialization creates outcomes directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            outcomes_dir = Path(tmpdir) / "test_outcomes"
            tracker = ReasoningOutcomeTracker(outcomes_dir=outcomes_dir)
            assert outcomes_dir.exists()
            assert outcomes_dir.is_dir()

    def test_record_outcome_in_memory(self):
        """Happy path: record_outcome stores outcome in memory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ReasoningOutcomeTracker(outcomes_dir=Path(tmpdir))
            outcome = ReasoningOutcome.create(
                trace_id="test-1",
                profile_hash="hash-1",
                complexity_tier="moderate",
                path_id="cot",
                latency_ms=100.0,
                tokens_used=50,
            )
            tracker.record_outcome(outcome)
            assert len(tracker._outcomes) == 1
            assert tracker._outcomes[0].trace_id == "test-1"

    def test_record_outcome_persists_to_disk(self):
        """Happy path: record_outcome persists to JSONL file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ReasoningOutcomeTracker(outcomes_dir=Path(tmpdir))
            outcome = ReasoningOutcome.create(
                trace_id="test-2",
                profile_hash="hash-2",
                complexity_tier="complex",
                path_id="tot",
                latency_ms=200.0,
                tokens_used=100,
            )
            tracker.record_outcome(outcome)

            # Check file was created
            date_str = time.strftime("%Y%m%d")
            daily_file = Path(tmpdir) / f"outcomes_{date_str}.jsonl"
            assert daily_file.exists()

            # Check content
            with open(daily_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                assert len(lines) == 1
                data = json.loads(lines[0])
                assert data["trace_id"] == "test-2"
                assert data["complexity_tier"] == "complex"

    def test_get_aggregates_basic(self):
        """Happy path: get_aggregates returns correct aggregation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ReasoningOutcomeTracker(outcomes_dir=Path(tmpdir))

            # Record 5 outcomes for same tier/path
            for i in range(5):
                outcome = ReasoningOutcome.create(
                    trace_id=f"agg-{i}",
                    profile_hash="hash-agg",
                    complexity_tier="moderate",
                    path_id="cot",
                    latency_ms=100.0 + i * 10,  # 100, 110, 120, 130, 140
                    tokens_used=50 + i * 5,  # 50, 55, 60, 65, 70
                    quality_score=0.8,
                )
                tracker.record_outcome(outcome)

            aggregates = tracker.get_aggregates(window_seconds=300, min_samples=5)
            assert len(aggregates) == 1
            agg = aggregates[0]
            assert agg.complexity_tier == "moderate"
            assert agg.path_id == "cot"
            assert agg.total_calls == 5
            assert agg.avg_latency_ms == 120.0  # (100+110+120+130+140)/5
            assert agg.avg_tokens == 60.0  # (50+55+60+65+70)/5
            assert agg.avg_quality_score == 0.8
            assert agg.error_rate == 0.0

    def test_get_aggregates_with_errors(self):
        """Edge case: get_aggregates correctly calculates error rate."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ReasoningOutcomeTracker(outcomes_dir=Path(tmpdir))

            # Record 5 outcomes: 2 errors, 3 success
            for i in range(5):
                outcome = ReasoningOutcome.create(
                    trace_id=f"err-{i}",
                    profile_hash="hash-err",
                    complexity_tier="complex",
                    path_id="tot",
                    latency_ms=100.0,
                    tokens_used=50,
                    error_type="TimeoutError" if i < 2 else None,
                )
                tracker.record_outcome(outcome)

            aggregates = tracker.get_aggregates(window_seconds=300, min_samples=5)
            assert len(aggregates) == 1
            assert aggregates[0].error_rate == 0.4  # 2/5 errors

    def test_get_aggregates_min_samples_filter(self):
        """Edge case: aggregates filters groups below min_samples."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ReasoningOutcomeTracker(outcomes_dir=Path(tmpdir))

            # Record 3 outcomes for one tier, 5 for another
            for i in range(3):
                outcome = ReasoningOutcome.create(
                    trace_id=f"low-{i}",
                    profile_hash="hash-low",
                    complexity_tier="simple",
                    path_id="cot",
                    latency_ms=100.0,
                    tokens_used=50,
                )
                tracker.record_outcome(outcome)

            for i in range(5):
                outcome = ReasoningOutcome.create(
                    trace_id=f"high-{i}",
                    profile_hash="hash-high",
                    complexity_tier="complex",
                    path_id="tot",
                    latency_ms=200.0,
                    tokens_used=100,
                )
                tracker.record_outcome(outcome)

            # min_samples=5 should filter out "simple" tier
            aggregates = tracker.get_aggregates(window_seconds=300, min_samples=5)
            assert len(aggregates) == 1
            assert aggregates[0].complexity_tier == "complex"

    def test_get_aggregates_window_filtering(self):
        """Edge case: aggregates filters by time window."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ReasoningOutcomeTracker(outcomes_dir=Path(tmpdir))

            # Record outcomes with timestamps manually set in the past
            old_outcome = ReasoningOutcome(
                trace_id="old",
                timestamp=time.time() - 600,  # 10 minutes ago
                profile_hash="hash-old",
                complexity_tier="moderate",
                path_id="cot",
                latency_ms=100.0,
                tokens_used=50,
            )
            tracker._outcomes.append(old_outcome)

            new_outcome = ReasoningOutcome(
                trace_id="new",
                timestamp=time.time(),  # now
                profile_hash="hash-new",
                complexity_tier="moderate",
                path_id="cot",
                latency_ms=200.0,
                tokens_used=100,
            )
            tracker._outcomes.append(new_outcome)

            # 300 second window should only include "new"
            aggregates = tracker.get_aggregates(window_seconds=300, min_samples=1)
            assert len(aggregates) == 1
            assert aggregates[0].avg_latency_ms == 200.0  # Only "new" included

    def test_get_aggregates_p95_calculation(self):
        """Edge case: p95 latency calculation is correct."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ReasoningOutcomeTracker(outcomes_dir=Path(tmpdir))

            # Record 20 outcomes with known latencies
            latencies = list(range(100, 300, 10))  # 100, 110, ..., 290
            for i, lat in enumerate(latencies):
                outcome = ReasoningOutcome.create(
                    trace_id=f"p95-{i}",
                    profile_hash="hash-p95",
                    complexity_tier="deep",
                    path_id="reflexion",
                    latency_ms=float(lat),
                    tokens_used=50,
                )
                tracker.record_outcome(outcome)

            aggregates = tracker.get_aggregates(window_seconds=300, min_samples=1)
            assert len(aggregates) == 1
            # p95 of 20 items: index 19 (0-indexed), which is latencies[19] = 290
            assert aggregates[0].p95_latency_ms == 290.0

    def test_memory_pruning(self):
        """Edge case: memory prunes when exceeding MAX_OUTCOMES."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ReasoningOutcomeTracker(outcomes_dir=Path(tmpdir))

            # Record more than MAX_OUTCOMES (10000)
            for i in range(10100):
                outcome = ReasoningOutcome.create(
                    trace_id=f"prune-{i}",
                    profile_hash="hash-prune",
                    complexity_tier="moderate",
                    path_id="cot",
                    latency_ms=100.0,
                    tokens_used=50,
                )
                tracker.record_outcome(outcome)

            # Should have been pruned to ~5000
            assert len(tracker._outcomes) < 6000
            assert len(tracker._outcomes) > 4000

    def test_export_aggregates_json(self):
        """Happy path: export_aggregates_json returns valid JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ReasoningOutcomeTracker(outcomes_dir=Path(tmpdir))

            for i in range(5):
                outcome = ReasoningOutcome.create(
                    trace_id=f"export-{i}",
                    profile_hash="hash-export",
                    complexity_tier="moderate",
                    path_id="cot",
                    latency_ms=100.0,
                    tokens_used=50,
                )
                tracker.record_outcome(outcome)

            json_str = tracker.export_aggregates_json()
            data = json.loads(json_str)
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]["complexity_tier"] == "moderate"

    def test_get_outcome_stats(self):
        """Happy path: get_outcome_stats returns correct info."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ReasoningOutcomeTracker(outcomes_dir=Path(tmpdir))

            for i in range(3):
                outcome = ReasoningOutcome.create(
                    trace_id=f"stats-{i}",
                    profile_hash="hash-stats",
                    complexity_tier="simple",
                    path_id="cot",
                    latency_ms=100.0,
                    tokens_used=50,
                )
                tracker.record_outcome(outcome)

            stats = tracker.get_outcome_stats()
            assert stats["total_outcomes_in_memory"] == 3
            assert stats["outcomes_dir"] == str(tracker._outcomes_dir)

    def test_persistence_with_file_error(self):
        """Failure path: handles file write errors gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ReasoningOutcomeTracker(outcomes_dir=Path(tmpdir))

            # Make directory read-only to cause permission error
            os.chmod(tmpdir, 0o444)

            try:
                outcome = ReasoningOutcome.create(
                    trace_id="error-test",
                    profile_hash="hash-error",
                    complexity_tier="moderate",
                    path_id="cot",
                    latency_ms=100.0,
                    tokens_used=50,
                )
                # Should not raise - error is silently swallowed in current implementation
                # This test documents the current behavior; improvement would be to add error handling
                tracker.record_outcome(outcome)
            finally:
                os.chmod(tmpdir, 0o755)


class TestOutcomeAggregate:
    """Test OutcomeAggregate dataclass."""

    def test_aggregate_creation(self):
        """Happy path: create aggregate manually."""
        agg = OutcomeAggregate(
            complexity_tier="complex",
            path_id="tot",
            total_calls=10,
            avg_latency_ms=150.0,
            avg_tokens=75.0,
            avg_quality_score=0.85,
            error_rate=0.1,
            p95_latency_ms=250.0,
            timestamp=time.time(),
        )
        assert agg.complexity_tier == "complex"
        assert agg.total_calls == 10
        assert agg.error_rate == 0.1

    def test_aggregate_without_quality_score(self):
        """Edge case: aggregate with None quality score."""
        agg = OutcomeAggregate(
            complexity_tier="simple",
            path_id="cot",
            total_calls=5,
            avg_latency_ms=50.0,
            avg_tokens=25.0,
            avg_quality_score=None,
            error_rate=0.0,
            p95_latency_ms=75.0,
            timestamp=time.time(),
        )
        assert agg.avg_quality_score is None
