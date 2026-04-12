"""C3 Failure Signal - Context-only failure detection.

10C-REQ-135: Build from context only no external hallucinated state
metadata check_id retry_count error_code lineage_hash
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class HealFailureClass(str, Enum):
    """C3 ALLOWLIST GATE failure classification passed to SCORE HEAL CONFIDENCE."""

    DRIFT_DETECTION = "DRIFT_DETECTION"
    IMPORT_BOUNDARY = "IMPORT_BOUNDARY"
    LAYER_INVERSION = "LAYER_INVERSION"
    SSOT_DRIFT = "SSOT_DRIFT"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class FailureSignal:
    """Immutable failure signal from execution context.

    10C-REQ-135: Built from context only - no external hallucinated state.
    """

    check_id: str
    retry_count: int
    error_code: str
    error_message: str
    lineage_hash: str
    context_snapshot: dict[str, Any]
    source_layer: str
    operation: str
    timestamp: float
    signal_hash: str = ""
    failure_class: HealFailureClass = HealFailureClass.UNKNOWN
    budget_remaining: float = 1.0

    def __post_init__(self) -> None:
        if not self.signal_hash:
            object.__setattr__(self, "signal_hash", self._compute_hash())

    def _compute_hash(self) -> str:
        """Compute deterministic hash of signal."""
        data = {
            "check_id": self.check_id,
            "retry_count": self.retry_count,
            "error_code": self.error_code,
            "lineage_hash": self.lineage_hash,
            "source_layer": self.source_layer,
            "operation": self.operation,
            "timestamp": self.timestamp,
            "failure_class": self.failure_class.name,
            "budget_remaining": self.budget_remaining,
        }
        raw = json.dumps(data, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


class FailureSignalBuilder:
    """Builder for failure signals from context only.

    10C-REQ-135: Build failure signal from context only no external
    hallucinated state metadata check_id retry_count error_code lineage_hash.
    """

    def __init__(self) -> None:
        self._context: dict[str, Any] = {}
        self._check_id: str = ""
        self._retry_count: int = 0
        self._error_code: str = ""
        self._error_message: str = ""
        self._lineage_hash: str = ""
        self._source_layer: str = ""
        self._operation: str = ""
        self._failure_class: HealFailureClass = HealFailureClass.UNKNOWN
        self._budget_remaining: float = 1.0

    def from_context(self, context: dict[str, Any]) -> FailureSignalBuilder:
        """Set context (source of truth - no external lookup)."""
        self._context = context.copy()
        return self

    def with_check(self, check_id: str, retry_count: int) -> FailureSignalBuilder:
        """Set check identification."""
        self._check_id = check_id
        self._retry_count = retry_count
        return self

    def with_error(self, code: str, message: str) -> FailureSignalBuilder:
        """Set error details."""
        self._error_code = code
        self._error_message = message
        return self

    def with_lineage(self, lineage_hash: str) -> FailureSignalBuilder:
        """Set lineage hash for traceability."""
        self._lineage_hash = lineage_hash
        return self

    def from_layer(self, layer: str, operation: str) -> FailureSignalBuilder:
        """Set source layer and operation."""
        self._source_layer = layer
        self._operation = operation
        return self

    def with_failure_class(self, failure_class: HealFailureClass) -> FailureSignalBuilder:
        """Set C3 ALLOWLIST GATE failure classification."""
        self._failure_class = failure_class
        return self

    def with_budget_remaining(self, budget: float) -> FailureSignalBuilder:
        """Set remaining execution budget fraction from E1 env/caps freeze."""
        self._budget_remaining = budget
        return self

    def build(self) -> FailureSignal:
        """Build failure signal from captured context."""
        if not self._check_id:
            raise ValueError("check_id required - cannot hallucinate")

        return FailureSignal(
            check_id=self._check_id,
            retry_count=self._retry_count,
            error_code=self._error_code,
            error_message=self._error_message,
            lineage_hash=self._lineage_hash,
            context_snapshot=self._context,
            source_layer=self._source_layer,
            operation=self._operation,
            timestamp=time.time(),
            failure_class=self._failure_class,
            budget_remaining=self._budget_remaining,
        )
