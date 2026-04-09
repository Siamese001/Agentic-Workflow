"""C3 Failure Signal - Context-only failure detection.

10C-REQ-135: Build from context only no external hallucinated state
metadata check_id retry_count error_code lineage_hash
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any


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

    def __post_init__(self) -> None:
        if not self.signal_hash:
            object.__setattr__(
                self,
                "signal_hash",
                self._compute_hash()
            )

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
        )
