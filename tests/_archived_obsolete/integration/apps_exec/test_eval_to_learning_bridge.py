"""
tests/integration/test_eval_to_learning_bridge.py

Integration test for Wave 1.1: Evaluation→Learning Feedback Bridge.

Tests the complete flow:
  eval_signal → evaluation_learning_bridge → meta_learning_bus → state update

Validates:
- BUS P (Preference: Eval → ML) implementation
- ADG edges: feeds_meta_learning (L6 → system_learning)
- Evaluation signal filtering (score >= 0.7)
- Learning event transformation
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import pytest

from agentic_core.L6_observability.utils.evaluation.evaluation_learning_bridge import (
    EvaluationLearningBridge,
    LearningEvent,
    get_evaluation_learning_bridge,
    reset_evaluation_learning_bridge,
)
from agentic_core.L6_system_learning.meta_learning_bus import MetaLearningBus


@dataclass
class MockEvalSignal:
    """Mock evaluation signal for testing."""

    trace_id: str
    source_module: str
    target_layer: str
    kind: Any
    score: float
    label: str
    metadata: dict[str, Any]


class MockEvalSignalKind:
    """Mock evaluation signal kind enum."""

    def __init__(self, value: str):
        self.value = value


class TestEvaluationLearningBridge:
    """Test suite for evaluation→learning bridge integration."""

    def test_bridge_transforms_signal_to_learning_event(self):
        """Test that bridge transforms eval signal to learning event."""
        bridge = EvaluationLearningBridge()

        eval_signal = MockEvalSignal(
            trace_id="trace-001",
            source_module="test_module",
            target_layer="L1",
            kind=MockEvalSignalKind("quality_score"),
            score=0.85,
            label="high_quality",
            metadata={"test": "data"},
        )

        learning_event = bridge._transform_signal_to_learning_event(
            eval_signal,
            timestamp_utc=1700000000.0,
        )

        assert isinstance(learning_event, LearningEvent)
        assert learning_event.trace_id == "trace-001"
        assert learning_event.source_module == "test_module"
        assert learning_event.target_layer == "L1"
        assert learning_event.eval_kind == "quality_score"
        assert learning_event.eval_score == 0.85
        assert learning_event.eval_label == "high_quality"
        assert learning_event.is_high_quality is True
        assert learning_event.is_learning_eligible is True

    def test_bridge_filters_low_quality_evaluations(self):
        """Test that bridge filters evaluations with score < 0.7."""
        bridge = EvaluationLearningBridge()

        # Low quality signal (score < 0.7)
        low_quality_signal = MockEvalSignal(
            trace_id="trace-002",
            source_module="test_module",
            target_layer="L1",
            kind=MockEvalSignalKind("quality_score"),
            score=0.5,
            label="low_quality",
            metadata={},
        )

        result = bridge.feed_evaluation_to_learning(low_quality_signal)

        assert result is None
        assert bridge.get_stats()["filter_count"] == 1
        assert bridge.get_stats()["feed_count"] == 0

    def test_bridge_feeds_high_quality_evaluations(self):
        """Test that bridge feeds evaluations with score >= 0.7."""
        bridge = EvaluationLearningBridge()

        # High quality signal (score >= 0.7)
        high_quality_signal = MockEvalSignal(
            trace_id="trace-003",
            source_module="test_module",
            target_layer="L2",
            kind=MockEvalSignalKind("faithfulness"),
            score=0.9,
            label="faithful",
            metadata={"context": "test"},
        )

        result = bridge.feed_evaluation_to_learning(high_quality_signal)

        assert result is not None
        assert isinstance(result, LearningEvent)
        assert result.eval_score == 0.9
        assert bridge.get_stats()["feed_count"] == 1
        assert bridge.get_stats()["filter_count"] == 0

    def test_bridge_stores_learning_events(self):
        """Test that bridge stores all learning events."""
        bridge = EvaluationLearningBridge()

        signals = [
            MockEvalSignal(
                trace_id=f"trace-{i:03d}",
                source_module="test_module",
                target_layer="L1",
                kind=MockEvalSignalKind("quality_score"),
                score=0.7 + (i * 0.05),
                label=f"event_{i}",
                metadata={},
            )
            for i in range(5)
        ]

        for signal in signals:
            bridge.feed_evaluation_to_learning(signal)

        events = bridge.get_learning_events()
        assert len(events) == 5
        assert all(isinstance(e, LearningEvent) for e in events)
        # Use pytest.approx for floating-point comparison
        assert [e.eval_score for e in events] == pytest.approx([0.7, 0.75, 0.8, 0.85, 0.9])

    def test_bridge_fail_open_on_error(self):
        """Test that bridge fails open on transformation errors."""
        bridge = EvaluationLearningBridge()

        # Invalid signal (missing attributes)
        invalid_signal = object()

        result = bridge.feed_evaluation_to_learning(invalid_signal)

        # Should return None but not raise exception
        assert result is None

    def test_global_bridge_singleton(self):
        """Test global bridge singleton pattern."""
        reset_evaluation_learning_bridge()

        bridge1 = get_evaluation_learning_bridge()
        bridge2 = get_evaluation_learning_bridge()

        assert bridge1 is bridge2

        # Reset and get new instance
        reset_evaluation_learning_bridge()
        bridge3 = get_evaluation_learning_bridge()

        assert bridge3 is not bridge1


class TestMetaLearningBusIntegration:
    """Test suite for meta learning bus integration."""

    def test_bus_consumes_evaluation_signal(self):
        """Test that meta learning bus consumes evaluation signals."""
        bus = MetaLearningBus()

        learning_event = LearningEvent(
            trace_id="trace-001",
            source_module="test_module",
            target_layer="L1",
            eval_kind="quality_score",
            eval_score=0.85,
            eval_label="high_quality",
            timestamp_utc=time.time(),
            metadata={},
        )

        bus.consume_evaluation_signal(learning_event)

        assert len(bus._evaluation_signals) == 1
        assert bus._evaluation_signals[0] == learning_event

    def test_bus_consumes_multiple_signals(self):
        """Test that bus accumulates multiple evaluation signals."""
        bus = MetaLearningBus()

        signals = [
            LearningEvent(
                trace_id=f"trace-{i:03d}",
                source_module="test_module",
                target_layer="L1",
                eval_kind="quality_score",
                eval_score=0.7 + (i * 0.05),
                eval_label=f"event_{i}",
                timestamp_utc=time.time(),
                metadata={},
            )
            for i in range(3)
        ]

        for signal in signals:
            bus.consume_evaluation_signal(signal)

        assert len(bus._evaluation_signals) == 3


class TestEndToEndIntegration:
    """End-to-end integration tests for eval→learning flow."""

    def test_complete_eval_to_learning_flow(self):
        """Test complete flow: eval signal → bridge → bus → state update."""
        # Setup
        reset_evaluation_learning_bridge()
        bridge = get_evaluation_learning_bridge()
        bus = MetaLearningBus()

        # Create evaluation signal
        eval_signal = MockEvalSignal(
            trace_id="trace-e2e-001",
            source_module="test_module",
            target_layer="L2",
            kind=MockEvalSignalKind("faithfulness"),
            score=0.92,
            label="high_faithfulness",
            metadata={"context_chunks": 5},
        )

        # Step 1: Bridge transforms and feeds to learning
        learning_event = bridge.feed_evaluation_to_learning(eval_signal)

        assert learning_event is not None
        assert learning_event.eval_score == 0.92
        assert learning_event.is_learning_eligible is True

        # Step 2: Bus consumes learning event
        bus.consume_evaluation_signal(learning_event)

        assert len(bus._evaluation_signals) == 1
        consumed_event = bus._evaluation_signals[0]
        assert consumed_event.trace_id == "trace-e2e-001"
        assert consumed_event.eval_score == 0.92

    def test_low_quality_filtered_from_learning(self):
        """Test that low-quality evals are filtered and don't reach bus."""
        reset_evaluation_learning_bridge()
        bridge = get_evaluation_learning_bridge()
        bus = MetaLearningBus()

        # Mix of high and low quality signals
        signals = [
            MockEvalSignal(
                trace_id=f"trace-{i:03d}",
                source_module="test_module",
                target_layer="L1",
                kind=MockEvalSignalKind("quality_score"),
                score=0.5 + (i * 0.1),  # 0.5, 0.6, 0.7, 0.8, 0.9
                label=f"event_{i}",
                metadata={},
            )
            for i in range(5)
        ]

        # Feed all signals through bridge
        for signal in signals:
            learning_event = bridge.feed_evaluation_to_learning(signal)
            if learning_event is not None:
                bus.consume_evaluation_signal(learning_event)

        # Only 3 signals should reach bus (scores 0.7, 0.8, 0.9)
        assert len(bus._evaluation_signals) == 3
        assert all(e.eval_score >= 0.7 for e in bus._evaluation_signals)

        # Bridge stats should show filtering
        stats = bridge.get_stats()
        assert stats["feed_count"] == 3
        assert stats["filter_count"] == 2
        assert stats["filter_rate"] == 0.4  # 2 filtered out of 5 total

    def test_evaluation_context_preserved_through_pipeline(self):
        """Test that evaluation metadata is preserved through the pipeline."""
        reset_evaluation_learning_bridge()
        bridge = get_evaluation_learning_bridge()
        bus = MetaLearningBus()

        eval_signal = MockEvalSignal(
            trace_id="trace-metadata-001",
            source_module="rag_module",
            target_layer="L2",
            kind=MockEvalSignalKind("context_precision"),
            score=0.88,
            label="precise_context",
            metadata={
                "retrieved_chunks": 10,
                "relevant_chunks": 9,
                "precision": 0.9,
                "query_type": "complex",
            },
        )

        learning_event = bridge.feed_evaluation_to_learning(eval_signal)
        bus.consume_evaluation_signal(learning_event)

        consumed = bus._evaluation_signals[0]
        assert consumed.metadata["retrieved_chunks"] == 10
        assert consumed.metadata["relevant_chunks"] == 9
        assert consumed.metadata["query_type"] == "complex"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
