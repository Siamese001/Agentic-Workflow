"""Risk correlation types for deterministic multi-signal correlation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass


@dataclass(frozen=True)
class DriftEvent:
    """A drift event for correlation analysis."""

    policy_id: str
    drift_type: str
    severity: float


@dataclass(frozen=True)
class CorrelatedRow:
    """A single correlation row between a fingerprint and a drift event."""

    fingerprint: str
    policy_id: str
    drift_type: str
    severity: float


@dataclass(frozen=True)
class CorrelatedRiskReport:
    """Deterministic report of correlated risks with canonical fingerprint."""

    rows: list[CorrelatedRow]
    correlation_fingerprint: str
    canonical_bytes: bytes

    @classmethod
    def from_canonical_bytes(
        cls,
        rows: list[CorrelatedRow],
        canonical_bytes: bytes,
    ) -> CorrelatedRiskReport:
        """Create report from canonical bytes."""
        correlation_fingerprint = hashlib.sha256(canonical_bytes).hexdigest()
        return cls(
            rows=rows,
            correlation_fingerprint=correlation_fingerprint,
            canonical_bytes=canonical_bytes,
        )


__all__ = ["CorrelatedRiskReport", "CorrelatedRow", "DriftEvent"]
