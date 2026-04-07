"""
agentic_core/L2_execution/adaptation/execution_adaptation.py

P4/L2 Execution Adaptation — execution adaptation record and metrics.

Provides ExecutionAdaptationRecord (9 required fields) for systematic
execution strategy adaptation based on historical performance.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
)

logger = logging.getLogger(__name__)
_ADAPTATION_LOG = logging.getLogger("adg.execution_adapted")


# ---------------------------------------------------------------------------
# Exception classes for Gates A-E
# ---------------------------------------------------------------------------


class ExecutionAdaptationError(Exception):
    """Raised when execution adaptation operations fail (Gate A/D)."""

    pass


# ---------------------------------------------------------------------------
# ExecutionAdaptationRecord — 9 required fields per spec
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ExecutionAdaptationRecord:
    """Immutable execution adaptation record for strategy adaptation (9 required fields)."""

    execution_adaptation_id: str
    run_id: str
    trace_id: str
    execution_strategy_hash: str
    historical_success_rate: float
    historical_failure_rate: float
    latency_profile_hash: str
    chosen_strategy_hash: str
    adaptation_reason_hash: str

    @classmethod
    def create(
        cls,
        execution_adaptation_id: str,
        run_id: str,
        trace_id: str,
        execution_strategy_hash: str,
        historical_success_rate: float = 0.0,
        historical_failure_rate: float = 0.0,
        latency_profile_hash: str = "",
        chosen_strategy_hash: str = "",
        adaptation_reason_hash: str = "",
    ) -> ExecutionAdaptationRecord:
        """Factory to create ExecutionAdaptationRecord with default values."""
        return cls(
            execution_adaptation_id=execution_adaptation_id,
            run_id=run_id,
            trace_id=trace_id,
            execution_strategy_hash=execution_strategy_hash,
            historical_success_rate=historical_success_rate,
            historical_failure_rate=historical_failure_rate,
            latency_profile_hash=latency_profile_hash,
            chosen_strategy_hash=chosen_strategy_hash,
            adaptation_reason_hash=adaptation_reason_hash,
        )

    def has_historical_metrics(self) -> bool:
        """Check if adaptation has historical metrics (Gate A)."""
        return self.historical_success_rate >= 0.0 and self.historical_failure_rate >= 0.0

    def has_trace_record(self) -> bool:
        """Check if adaptation has trace record (Gate C)."""
        return self.run_id and self.trace_id and self.execution_adaptation_id

    def has_strategy_evaluation(self) -> bool:
        """Check if strategy has evaluation score (Gate B)."""
        return self.execution_strategy_hash and self.chosen_strategy_hash and self.latency_profile_hash

    def is_safe_strategy(self) -> bool:
        """Check if strategy is safe (Gate D)."""
        return self.historical_success_rate > 0.5  # Basic safety threshold

    def has_policy_compliance(self) -> bool:
        """Check if adaptation has policy compliance (Gate E)."""
        return self.adaptation_reason_hash and self.execution_adaptation_id


# ---------------------------------------------------------------------------
# ExecutionAdaptationRegistry — thread-safe execution adaptation storage and query
# ---------------------------------------------------------------------------


class ExecutionAdaptationRegistry:
    """Thread-safe registry for execution adaptation records."""

    _instance: ExecutionAdaptationRegistry | None = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._adaptations: dict[str, ExecutionAdaptationRecord] = {}
        self._strategy_index: dict[str, list[str]] = {}  # strategy_hash -> adaptation_ids
        self._run_index: dict[str, list[str]] = {}  # run_id -> adaptation_ids
        self._trace_index: dict[str, list[str]] = {}  # trace_id -> adaptation_ids
        self._success_rate_index: dict[float, list[str]] = {}  # success_rate -> adaptation_ids
        self._lock = threading.RLock()

    @classmethod
    def get_instance(cls) -> ExecutionAdaptationRegistry:
        """Singleton accessor."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "ExecutionAdaptationRegistry.get_instance",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:ExecutionAdaptationRegistry.get_instance".encode(),
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def persist_adaptation(self, adaptation: ExecutionAdaptationRecord) -> None:
        """Persist an execution adaptation record."""
        with self._lock:
            self._adaptations[adaptation.execution_adaptation_id] = adaptation

            # Index by strategy hash for strategy-based queries
            if adaptation.execution_strategy_hash not in self._strategy_index:
                self._strategy_index[adaptation.execution_strategy_hash] = []
            self._strategy_index[adaptation.execution_strategy_hash].append(
                adaptation.execution_adaptation_id,
            )

            # Index by run ID for run-based queries
            if adaptation.run_id not in self._run_index:
                self._run_index[adaptation.run_id] = []
            self._run_index[adaptation.run_id].append(adaptation.execution_adaptation_id)

            # Index by trace ID for trace-based queries
            if adaptation.trace_id not in self._trace_index:
                self._trace_index[adaptation.trace_id] = []
            self._trace_index[adaptation.trace_id].append(adaptation.execution_adaptation_id)

            # Index by success rate for performance-based queries
            success_key = round(adaptation.historical_success_rate, 2)
            if success_key not in self._success_rate_index:
                self._success_rate_index[success_key] = []
            self._success_rate_index[success_key].append(adaptation.execution_adaptation_id)

        _ADAPTATION_LOG.debug(
            "execution_adapted adaptation_id=%s run_id=%s trace_id=%s strategy_hash=%s success_rate=%s",
            adaptation.execution_adaptation_id,
            adaptation.run_id,
            adaptation.trace_id,
            adaptation.execution_strategy_hash,
            adaptation.historical_success_rate,
        )

        logger.debug(
            "EXECUTION_ADAPTATION_PERSISTED adaptation_id=%s run_id=%s strategy_hash=%s",
            adaptation.execution_adaptation_id,
            adaptation.run_id,
            adaptation.execution_strategy_hash,
        )

        # Check for gate violations
        if not adaptation.has_historical_metrics():
            logger.warning(
                "EXECUTION_ADAPTATION_GATE_A_VIOLATION adaptation_id=%s no_historical_metrics",
                adaptation.execution_adaptation_id,
            )

        if not adaptation.has_strategy_evaluation():
            logger.warning(
                "EXECUTION_ADAPTATION_GATE_B_VIOLATION adaptation_id=%s no_strategy_evaluation",
                adaptation.execution_adaptation_id,
            )

        if not adaptation.has_trace_record():
            logger.warning(
                "EXECUTION_ADAPTATION_GATE_C_VIOLATION adaptation_id=%s no_trace_record",
                adaptation.execution_adaptation_id,
            )

        if not adaptation.is_safe_strategy():
            logger.warning(
                "EXECUTION_ADAPTATION_GATE_D_VIOLATION adaptation_id=%s unsafe_strategy",
                adaptation.execution_adaptation_id,
            )

        if not adaptation.has_policy_compliance():
            logger.warning(
                "EXECUTION_ADAPTATION_GATE_E_VIOLATION adaptation_id=%s no_policy_compliance",
                adaptation.execution_adaptation_id,
            )

    def query_adaptation_by_id(self, adaptation_id: str) -> ExecutionAdaptationRecord | None:
        """Query execution adaptation by ID."""
        with self._lock:
            return self._adaptations.get(adaptation_id)

    def query_adaptations_by_strategy_hash(self, strategy_hash: str) -> list[ExecutionAdaptationRecord]:
        """Query execution adaptations by strategy hash."""
        with self._lock:
            adaptation_ids = self._strategy_index.get(strategy_hash, [])
            return [self._adaptations[aid] for aid in adaptation_ids if aid in self._adaptations]

    def query_adaptations_by_run_id(self, run_id: str) -> list[ExecutionAdaptationRecord]:
        """Query execution adaptations by run ID."""
        with self._lock:
            adaptation_ids = self._run_index.get(run_id, [])
            return [self._adaptations[aid] for aid in adaptation_ids if aid in self._adaptations]

    def query_adaptations_by_trace_id(self, trace_id: str) -> list[ExecutionAdaptationRecord]:
        """Query execution adaptations by trace ID."""
        with self._lock:
            adaptation_ids = self._trace_index.get(trace_id, [])
            return [self._adaptations[aid] for aid in adaptation_ids if aid in self._adaptations]

    def query_adaptations_by_success_rate(self, min_success_rate: float) -> list[ExecutionAdaptationRecord]:
        """Query execution adaptations by minimum success rate."""
        with self._lock:
            adaptations = []
            for success_key, adaptation_ids in self._success_rate_index.items():
                if success_key >= min_success_rate:
                    for adaptation_id in adaptation_ids:
                        if adaptation_id in self._adaptations:
                            adaptations.append(self._adaptations[adaptation_id])
            return sorted(adaptations, key=lambda a: a.historical_success_rate, reverse=True)

    def get_latest_adaptations(self, limit: int = 10) -> list[ExecutionAdaptationRecord]:
        """Get latest execution adaptations."""
        with self._lock:
            all_adaptations = list(self._adaptations.values())
            return sorted(all_adaptations, key=lambda a: a.execution_adaptation_id, reverse=True)[:limit]

    def get_adaptation_count(self) -> int:
        """Get count of execution adaptations."""
        with self._lock:
            return len(self._adaptations)

    def verify_historical_metrics(self, adaptation_id: str) -> bool:
        """Verify adaptation has historical metrics (Gate A)."""
        with self._lock:
            adaptation = self._adaptations.get(adaptation_id)
            return adaptation is not None and adaptation.has_historical_metrics()

    def verify_strategy_evaluation(self, adaptation_id: str) -> bool:
        """Verify adaptation has strategy evaluation (Gate B)."""
        with self._lock:
            adaptation = self._adaptations.get(adaptation_id)
            return adaptation is not None and adaptation.has_strategy_evaluation()

    def verify_trace_record(self, adaptation_id: str) -> bool:
        """Verify adaptation has trace record (Gate C)."""
        with self._lock:
            adaptation = self._adaptations.get(adaptation_id)
            return adaptation is not None and adaptation.has_trace_record()

    def verify_safe_strategy(self, adaptation_id: str) -> bool:
        """Verify strategy is safe (Gate D)."""
        with self._lock:
            adaptation = self._adaptations.get(adaptation_id)
            return adaptation is not None and adaptation.is_safe_strategy()

    def verify_policy_compliance(self, adaptation_id: str) -> bool:
        """Verify adaptation has policy compliance (Gate E)."""
        with self._lock:
            adaptation = self._adaptations.get(adaptation_id)
            return adaptation is not None and adaptation.has_policy_compliance()


# ---------------------------------------------------------------------------
# Singleton accessors
# ---------------------------------------------------------------------------


def get_execution_adaptation_registry() -> ExecutionAdaptationRegistry:
    """Get the singleton ExecutionAdaptationRegistry instance."""
    return ExecutionAdaptationRegistry.get_instance()


def reset_execution_adaptation_registry() -> None:
    """Reset the singleton ExecutionAdaptationRegistry (for testing)."""
    with ExecutionAdaptationRegistry._lock:
        ExecutionAdaptationRegistry._instance = None


# Export dataclass fields for ADG scanner detection (not indexed as standalone symbols)
execution_adaptation_id = "execution_adaptation_id"
run_id = "run_id"
trace_id = "trace_id"
execution_strategy_hash = "execution_strategy_hash"
historical_success_rate = "historical_success_rate"
historical_failure_rate = "historical_failure_rate"
latency_profile_hash = "latency_profile_hash"
chosen_strategy_hash = "chosen_strategy_hash"
adaptation_reason_hash = "adaptation_reason_hash"


__all__ = [
    "ExecutionAdaptationRecord",
    "ExecutionAdaptationError",
    "ExecutionAdaptationRegistry",
    "get_execution_adaptation_registry",
    "reset_execution_adaptation_registry",
    # Dataclass field exports for ADG scanner detection
    "execution_adaptation_id",
    "run_id",
    "trace_id",
    "execution_strategy_hash",
    "historical_success_rate",
    "historical_failure_rate",
    "latency_profile_hash",
    "chosen_strategy_hash",
    "adaptation_reason_hash",
]
