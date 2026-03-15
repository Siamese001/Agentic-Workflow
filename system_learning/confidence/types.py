"""Healing confidence scoring types for deterministic escalation decisions."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


@dataclass(frozen=True)
class HealingAttempt:
    """A healing attempt for confidence scoring."""

    attempt_id: str
    healer_id: str
    outcome: str
    severity: int
    signals: dict[str, str]
    cost: float

    def canonical_bytes(self) -> bytes:
        """Canonical byte representation for deterministic fingerprinting."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HealingAttempt.canonical_bytes")

        data = {
            "attempt_id": self.attempt_id,
            "healer_id": self.healer_id,
            "outcome": self.outcome,
            "severity": self.severity,
            "signals": {k: str(v) for k, v in sorted(self.signals.items())},
            "cost": self.cost,
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")


@dataclass(frozen=True)
class ConfidenceDecision:
    """Confidence decision for a healing attempt."""

    attempt_id: str
    confidence: float
    action: str


@dataclass(frozen=True)
class HealingConfidenceReport:
    """Report of healing confidence scoring with deterministic fingerprint."""

    decisions: list[ConfidenceDecision]
    confidence_fingerprint: str
    canonical_bytes: bytes

    @classmethod
    def from_canonical_bytes(
        cls, decisions: list[ConfidenceDecision], canonical_bytes: bytes
    ) -> HealingConfidenceReport:
        """Create report from canonical bytes."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HealingConfidenceReport.from_canonical_bytes")

        confidence_fingerprint = hashlib.sha256(canonical_bytes).hexdigest()
        return cls(
            decisions=decisions,
            confidence_fingerprint=confidence_fingerprint,
            canonical_bytes=canonical_bytes,
        )
