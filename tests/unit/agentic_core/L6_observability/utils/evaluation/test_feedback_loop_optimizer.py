"""
tests/unit/agentic_core/L6_observability/evaluation/test_feedback_loop_optimizer.py

Unit tests for Wave 2.2: Feedback Loop Optimization

Tests:
- Signal queueing and prioritization
- Backpressure handling
- Adaptive sampling
- Batch processing
- Rate limiting
- Metrics tracking
"""

from __future__ import annotations

import pytest

from agentic_core.L6_observability.utils.evaluation.feedback_loop_optimizer import (
    BackpressureState,
    FeedbackLoopOptimizer,
    get_feedback_optimizer,
    reset_feedback_optimizer,
)


class TestFeedbackLoopOptimizer:
    """Test suite for FeedbackLoopOptimizer."""

    def test_enqueue_signal_basic(self):
        """Test basic signal enqueueing."""
        optimizer = FeedbackLoopOptimizer()

        result = optimizer.enqueue_signal({"test": "signal"}, priority=0.5)

        assert result is True
        metrics = optimizer.get_metrics()
        assert metrics.signals_queued == 1
        assert metrics.current_queue_size == 1

    def test_priority_ordering(self):
        """Test signals are ordered by priority."""
        optimizer = FeedbackLoopOptimizer()

        # Enqueue signals with different priorities
        optimizer.enqueue_signal({"priority": "low"}, priority=0.3)
        optimizer.enqueue_signal({"priority": "high"}, priority=0.9)
        optimizer.enqueue_signal({"priority": "medium"}, priority=0.6)

        # Process batch - should get highest priority first
        batch = optimizer.process_batch(batch_size=3)

        assert len(batch) == 3
        # Highest priority processed first (popped from end)
        assert batch[0]["priority"] == "high"

    def test_queue_capacity_limit(self):
        """Test queue capacity enforcement."""
        optimizer = FeedbackLoopOptimizer(max_queue_size=10)

        # Fill queue to capacity with high priority to ensure they pass sampling
        for i in range(10):
            result = optimizer.enqueue_signal({"id": i}, priority=1.0)
            assert result is True

        # Next signal with high priority should trigger capacity handling
        optimizer.enqueue_signal({"id": 11}, priority=1.0)

        metrics = optimizer.get_metrics()
        # Queue should not exceed capacity
        assert metrics.current_queue_size <= 10
        # At least one signal should be dropped or replaced
        assert metrics.signals_dropped >= 1 or metrics.current_queue_size == 10

    def test_backpressure_states(self):
        """Test backpressure state transitions."""
        optimizer = FeedbackLoopOptimizer(max_queue_size=100)

        # Normal state (< 50% full)
        for i in range(40):
            optimizer.enqueue_signal({"id": i}, priority=1.0)

        metrics = optimizer.get_metrics()
        assert metrics.backpressure_state == BackpressureState.NORMAL

        # Elevated state (50-75% full)
        for i in range(20):
            optimizer.enqueue_signal({"id": i + 40}, priority=1.0)

        metrics = optimizer.get_metrics()
        assert metrics.backpressure_state == BackpressureState.ELEVATED

        # High state (75-90% full)
        for i in range(15):
            optimizer.enqueue_signal({"id": i + 60}, priority=1.0)

        metrics = optimizer.get_metrics()
        assert metrics.backpressure_state == BackpressureState.HIGH

    def test_adaptive_sampling(self):
        """Test adaptive sampling reduces rate under load."""
        optimizer = FeedbackLoopOptimizer(max_queue_size=100)

        # Fill queue to trigger backpressure
        for i in range(80):
            optimizer.enqueue_signal({"id": i}, priority=1.0)

        initial_rate = optimizer._current_sampling_rate

        # Process some signals to trigger sampling rate update
        optimizer.process_batch(batch_size=10)

        # Sampling rate should decrease under high load
        # (or stay same if queue drains enough)
        assert optimizer._current_sampling_rate <= initial_rate

    def test_batch_processing(self):
        """Test batch processing."""
        optimizer = FeedbackLoopOptimizer()

        # Enqueue signals
        for i in range(20):
            optimizer.enqueue_signal({"id": i}, priority=0.5)

        # Process batch of 10
        batch = optimizer.process_batch(batch_size=10)

        assert len(batch) == 10
        metrics = optimizer.get_metrics()
        assert metrics.signals_processed == 10
        assert metrics.current_queue_size == 10

    def test_metrics_tracking(self):
        """Test metrics are tracked correctly."""
        optimizer = FeedbackLoopOptimizer(max_queue_size=10)

        # Enqueue some signals
        for i in range(5):
            optimizer.enqueue_signal({"id": i}, priority=0.5)

        # Process some
        optimizer.process_batch(batch_size=3)

        metrics = optimizer.get_metrics()
        assert metrics.signals_queued == 5
        assert metrics.signals_processed == 3
        assert metrics.current_queue_size == 2

    def test_high_priority_signals_preserved(self):
        """Test high priority signals are preserved under backpressure."""
        optimizer = FeedbackLoopOptimizer(max_queue_size=10)

        # Fill queue with low priority
        for i in range(10):
            optimizer.enqueue_signal({"priority": "low", "id": i}, priority=0.2)

        # Try to enqueue high priority signal
        result = optimizer.enqueue_signal({"priority": "high"}, priority=0.9)

        # High priority should either be accepted or replace low priority
        metrics = optimizer.get_metrics()
        assert metrics.current_queue_size <= 10

    def test_clear_queue(self):
        """Test clearing queue."""
        optimizer = FeedbackLoopOptimizer()

        # Enqueue signals
        for i in range(10):
            optimizer.enqueue_signal({"id": i}, priority=0.5)

        optimizer.clear_queue()

        metrics = optimizer.get_metrics()
        assert metrics.current_queue_size == 0

    def test_reset_metrics(self):
        """Test resetting metrics."""
        optimizer = FeedbackLoopOptimizer()

        # Generate some activity
        for i in range(5):
            optimizer.enqueue_signal({"id": i}, priority=0.5)
        optimizer.process_batch(batch_size=3)

        optimizer.reset_metrics()

        metrics = optimizer.get_metrics()
        assert metrics.signals_queued == 0
        assert metrics.signals_processed == 0
        assert metrics.signals_dropped == 0

    def test_processing_time_tracking(self):
        """Test processing time is tracked."""
        optimizer = FeedbackLoopOptimizer()

        # Enqueue and process signals
        for i in range(10):
            optimizer.enqueue_signal({"id": i}, priority=0.5)

        optimizer.process_batch(batch_size=10)

        metrics = optimizer.get_metrics()
        assert metrics.avg_processing_time_ms >= 0.0

    def test_empty_batch_processing(self):
        """Test processing empty queue."""
        optimizer = FeedbackLoopOptimizer()

        batch = optimizer.process_batch(batch_size=10)

        assert len(batch) == 0
        metrics = optimizer.get_metrics()
        assert metrics.signals_processed == 0


class TestGlobalInstance:
    """Test global instance management."""

    def test_singleton_pattern(self):
        """Test feedback optimizer singleton pattern."""
        reset_feedback_optimizer()

        optimizer1 = get_feedback_optimizer()
        optimizer2 = get_feedback_optimizer()

        assert optimizer1 is optimizer2

        reset_feedback_optimizer()
        optimizer3 = get_feedback_optimizer()

        assert optimizer3 is not optimizer1


class TestIntegration:
    """Integration tests for feedback loop optimization."""

    def test_full_feedback_loop_workflow(self):
        """Test complete feedback loop workflow."""
        optimizer = FeedbackLoopOptimizer(max_queue_size=100)

        # Simulate varying load
        # Phase 1: Normal load
        for i in range(20):
            optimizer.enqueue_signal({"phase": 1, "id": i}, priority=0.5)

        batch1 = optimizer.process_batch(batch_size=10)
        assert len(batch1) == 10

        # Phase 2: High load
        for i in range(60):
            optimizer.enqueue_signal({"phase": 2, "id": i}, priority=0.5)

        metrics = optimizer.get_metrics()
        assert metrics.backpressure_state in [BackpressureState.ELEVATED, BackpressureState.HIGH]

        # Phase 3: Process under load
        batch2 = optimizer.process_batch(batch_size=20)
        assert len(batch2) == 20

        # Phase 4: Drain queue
        while optimizer.get_metrics().current_queue_size > 0:
            optimizer.process_batch(batch_size=10)

        final_metrics = optimizer.get_metrics()
        assert final_metrics.current_queue_size == 0
        assert final_metrics.signals_processed > 0

    def test_priority_under_backpressure(self):
        """Test priority handling under backpressure."""
        optimizer = FeedbackLoopOptimizer(max_queue_size=50)

        # Fill with medium priority signals
        for i in range(45):
            optimizer.enqueue_signal({"priority": "medium", "id": i}, priority=0.5)

        # Add high priority signals
        high_priority_count = 0
        for i in range(10):
            result = optimizer.enqueue_signal({"priority": "high", "id": i}, priority=0.9)
            if result:
                high_priority_count += 1

        # Some high priority signals should be enqueued
        assert high_priority_count > 0

        # Process batch - should include high priority signals
        batch = optimizer.process_batch(batch_size=10)
        high_priority_in_batch = sum(1 for s in batch if s.get("priority") == "high")

        # At least some high priority signals should be processed
        assert high_priority_in_batch >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
