"""Risk correlation types for deterministic multi-signal correlation."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class CorrelatedRow:
    """A correlated risk row linking fingerprint to drift events."""

    fingerprint: str
    policy_id: str
    drift_type: str
    severity: float


@dataclass(frozen=True)
class CorrelatedRiskReport:
    """Report of correlated risk analysis with deterministic fingerprint."""

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
