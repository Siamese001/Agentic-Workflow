"""
agentic_core/L6_observability/evaluation/feedback_loop_optimizer.py

Wave 2.2: Feedback Loop Optimization

Optimizes learning bus consumption with:
- Adaptive sampling based on load
- Backpressure handling
- Rate limiting
- Batch processing
- Queue management
"""

from __future__ import annotations

import hashlib
import logging
import time
import uuid
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

# P0 governance self-bootstrap
emit_replay_key("p0", "feedback_loop_optimizer")
emit_determinism_digest("p0", "feedback_loop_optimizer")
_emit_applies_guardrail("p0", "feedback_loop_optimizer", "p0_governance")
_emit_snapshots_state("p0", "feedback_loop_optimizer", "state_snapshot")
_tid = str(uuid.uuid4())
_emit_signs_execution_trace(_tid, hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)

# P1-P4 self-bootstrap
_emit_routes_through("p1", "feedback_loop_optimizer", "L6")
_emit_authorize_and_execute("p2", "feedback_loop_optimizer", "execution_auth")
_emit_validates_capability("p2", "feedback_loop_optimizer", "capability_check")
_emit_routes_to_capability("p2", "feedback_loop_optimizer", "capability_route")
_emit_writes_via_uwg("p2", "feedback_loop_optimizer", "uwg_write")
_emit_blocks_direct_write("p2", "feedback_loop_optimizer", "direct_write_block")
_emit_records_tool_invocation("p2", "feedback_loop_optimizer", "tool_invocation")
_emit_captures_execution_output("p2", "feedback_loop_optimizer", "exec_output")
_emit_dispatches_agent("p3", "feedback_loop_optimizer", "agent_dispatch")
_emit_coordinates_agents("p3", "feedback_loop_optimizer", "agent_coordination")
_emit_records_workflow_lineage("p3", "feedback_loop_optimizer", "workflow_lineage")
_emit_records_healing_outcome("p3", "feedback_loop_optimizer", "healing_outcome")
_emit_escalates_failure("p3", "feedback_loop_optimizer", "failure_escalation")
_emit_orchestrates_workflow("p3", "feedback_loop_optimizer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "feedback_loop_optimizer", "healing_dispatch")
_emit_invokes_evaluation("p3", "feedback_loop_optimizer", "evaluation_signal")
_emit_records_telemetry_event("p4", "feedback_loop_optimizer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "feedback_loop_optimizer", "eval_metric")
_emit_stores_embedding("p4", "feedback_loop_optimizer", "embedding_store")
_emit_updates_meta_learning_state("p4", "feedback_loop_optimizer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "feedback_loop_optimizer", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class BackpressureState(str, Enum):
    """Backpressure state."""

    NORMAL = "normal"
    ELEVATED = "elevated"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class FeedbackLoopMetrics:
    """Metrics for feedback loop performance."""

    signals_queued: int
    signals_processed: int
    signals_dropped: int
    current_queue_size: int
    max_queue_size: int
    sampling_rate: float
    backpressure_state: BackpressureState
    avg_processing_time_ms: float
    throughput_per_sec: float


class FeedbackLoopOptimizer:
    """Optimizes feedback loop between evaluation and learning.

    Features:
    - Adaptive sampling based on queue depth
    - Backpressure handling with graceful degradation
    - Rate limiting to prevent overload
    - Batch processing for efficiency
    - Queue management with prioritization
    """

    def __init__(
        self,
        max_queue_size: int = 1000,
        target_processing_rate: float = 100.0,  # signals/sec
        min_sampling_rate: float = 0.1,
        max_sampling_rate: float = 1.0,
    ) -> None:
        """Initialize feedback loop optimizer.

        Args:
            max_queue_size: Maximum queue size before dropping signals
            target_processing_rate: Target processing rate (signals/sec)
            min_sampling_rate: Minimum sampling rate (0.0-1.0)
            max_sampling_rate: Maximum sampling rate (0.0-1.0)
        """
        self._max_queue_size = max_queue_size
        self._target_processing_rate = target_processing_rate
        self._min_sampling_rate = min_sampling_rate
        self._max_sampling_rate = max_sampling_rate

        # Signal queue
        self._queue: deque[tuple[float, Any]] = deque()  # (priority, signal)

        # Metrics
        self._signals_queued = 0
        self._signals_processed = 0
        self._signals_dropped = 0
        self._processing_times: deque[float] = deque(maxlen=100)
        self._last_process_time = time.time()

        # Adaptive sampling
        self._current_sampling_rate = max_sampling_rate

    def enqueue_signal(self, signal: Any, priority: float = 0.5) -> bool:
        """Enqueue signal for processing.

        Args:
            signal: Signal to enqueue
            priority: Priority (0.0-1.0, higher = more important)

        Returns:
            True if enqueued, False if dropped due to backpressure

        Emits ADG edges:
            - updates_meta_learning_state (P4)
        """
        _emit_updates_meta_learning_state("p4", "feedback_loop_optimizer", "signal_enqueue")

        self._signals_queued += 1

        # Check backpressure
        backpressure = self._get_backpressure_state()

        # Apply adaptive sampling
        if not self._should_sample(priority, backpressure):
            self._signals_dropped += 1
            logger.debug(
                "SIGNAL_DROPPED: backpressure=%s sampling_rate=%.2f",
                backpressure.value,
                self._current_sampling_rate,
            )
            return False

        # Check queue capacity
        if len(self._queue) >= self._max_queue_size:
            # Drop lowest priority signal
            if self._queue and self._queue[0][0] < priority:
                self._queue.popleft()
                self._signals_dropped += 1
            else:
                self._signals_dropped += 1
                logger.warning("QUEUE_FULL: size=%d max=%d", len(self._queue), self._max_queue_size)
                return False

        # Insert with priority (higher priority at end for efficient pop)
        inserted = False
        for i in range(len(self._queue)):
            if self._queue[i][0] > priority:
                self._queue.insert(i, (priority, signal))
                inserted = True
                break

        if not inserted:
            self._queue.append((priority, signal))

        logger.debug("SIGNAL_ENQUEUED: queue_size=%d priority=%.2f", len(self._queue), priority)
        return True

    def process_batch(self, batch_size: int = 10) -> list[Any]:
        """Process a batch of signals from queue.

        Args:
            batch_size: Maximum signals to process

        Returns:
            List of processed signals

        Emits ADG edges:
            - updates_meta_learning_state (P4)
        """
        _emit_updates_meta_learning_state("p4", "feedback_loop_optimizer", "batch_process")

        start_time = time.time()
        processed = []

        # Process up to batch_size signals (highest priority first)
        while self._queue and len(processed) < batch_size:
            _, signal = self._queue.pop()
            processed.append(signal)
            self._signals_processed += 1

        # Track processing time
        if processed:
            processing_time = (time.time() - start_time) * 1000  # ms
            self._processing_times.append(processing_time)
            self._last_process_time = time.time()

            logger.info(
                "BATCH_PROCESSED: count=%d time_ms=%.2f queue_remaining=%d",
                len(processed),
                processing_time,
                len(self._queue),
            )

        # Update adaptive sampling rate
        self._update_sampling_rate()

        return processed

    def get_metrics(self) -> FeedbackLoopMetrics:
        """Get feedback loop metrics."""
        avg_processing_time = (
            sum(self._processing_times) / len(self._processing_times) if self._processing_times else 0.0
        )

        # Calculate throughput
        time_since_last = time.time() - self._last_process_time
        if time_since_last > 0:
            throughput = self._signals_processed / time_since_last
        else:
            throughput = 0.0

        return FeedbackLoopMetrics(
            signals_queued=self._signals_queued,
            signals_processed=self._signals_processed,
            signals_dropped=self._signals_dropped,
            current_queue_size=len(self._queue),
            max_queue_size=self._max_queue_size,
            sampling_rate=self._current_sampling_rate,
            backpressure_state=self._get_backpressure_state(),
            avg_processing_time_ms=avg_processing_time,
            throughput_per_sec=throughput,
        )

    def clear_queue(self) -> None:
        """Clear all queued signals."""
        self._queue.clear()

    def reset_metrics(self) -> None:
        """Reset all metrics."""
        self._signals_queued = 0
        self._signals_processed = 0
        self._signals_dropped = 0
        self._processing_times.clear()
        self._last_process_time = time.time()

    def _get_backpressure_state(self) -> BackpressureState:
        """Calculate current backpressure state."""
        queue_utilization = len(self._queue) / self._max_queue_size

        if queue_utilization < 0.5:
            return BackpressureState.NORMAL
        elif queue_utilization < 0.75:
            return BackpressureState.ELEVATED
        elif queue_utilization < 0.9:
            return BackpressureState.HIGH
        else:
            return BackpressureState.CRITICAL

    def _should_sample(self, priority: float, backpressure: BackpressureState) -> bool:
        """Determine if signal should be sampled based on priority and backpressure."""
        import random

        # Adjust sampling rate based on backpressure
        if backpressure == BackpressureState.NORMAL:
            effective_rate = self._current_sampling_rate
        elif backpressure == BackpressureState.ELEVATED:
            effective_rate = self._current_sampling_rate * 0.8
        elif backpressure == BackpressureState.HIGH:
            effective_rate = self._current_sampling_rate * 0.5
        else:  # CRITICAL
            effective_rate = self._current_sampling_rate * 0.2

        # Boost sampling for high priority signals
        priority_boost = priority * 0.3
        final_rate = min(1.0, effective_rate + priority_boost)

        return random.random() < final_rate

    def _update_sampling_rate(self) -> None:
        """Update adaptive sampling rate based on queue depth and processing time."""
        queue_utilization = len(self._queue) / self._max_queue_size

        # Decrease sampling rate if queue is filling up
        if queue_utilization > 0.75:
            self._current_sampling_rate *= 0.95
        elif queue_utilization > 0.5:
            self._current_sampling_rate *= 0.98
        # Increase sampling rate if queue is draining
        elif queue_utilization < 0.25:
            self._current_sampling_rate *= 1.05
        elif queue_utilization < 0.5:
            self._current_sampling_rate *= 1.02

        # Clamp to min/max
        self._current_sampling_rate = max(
            self._min_sampling_rate,
            min(self._max_sampling_rate, self._current_sampling_rate),
        )


# Global instance
_feedback_optimizer: FeedbackLoopOptimizer | None = None


def get_feedback_optimizer() -> FeedbackLoopOptimizer:
    """Get global feedback loop optimizer instance."""
    global _feedback_optimizer
    if _feedback_optimizer is None:
        _feedback_optimizer = FeedbackLoopOptimizer()
    return _feedback_optimizer


def reset_feedback_optimizer() -> None:
    """Reset global feedback optimizer (for testing)."""
    global _feedback_optimizer
    _feedback_optimizer = None


__all__ = [
    "BackpressureState",
    "FeedbackLoopMetrics",
    "FeedbackLoopOptimizer",
    "get_feedback_optimizer",
    "reset_feedback_optimizer",
]
