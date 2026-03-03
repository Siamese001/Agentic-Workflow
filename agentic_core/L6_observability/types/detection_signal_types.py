"""
L6 DetectionSignal — Phase 3

Non-authority passive detection signal emitted at mission boundary.
Carries scalar health metrics; persisted to L4 SSOT for N+1 routing influence.

AUTHORITY CONSTRAINT: DetectionSignal MUST NOT mutate current execution decisions.
It is emitted AFTER GatewayResult is finalized and cannot change it.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass
class DetectionSignal:
    """
    Scalar health metrics snapshot emitted at mission boundary.

    Fields:
        schema_version    — int, incremented on breaking changes
        mission_id        — str, identifies the mission/execution context
        created_at_utc    — int, UTC epoch seconds (stable, no sub-second noise)
        anomaly_score     — float [0..1], overall anomaly level
        escalation_rate   — float [0..1], fraction of steps that escalated
        retry_rate        — float [0..1], fraction of steps that retried
        violation_density — float [0..1], fraction of steps with violations
        signal_hash       — sha256 of canonical_bytes() excluding signal_hash itself
    """

    schema_version: int
    mission_id: str
    created_at_utc: int
    anomaly_score: float
    escalation_rate: float
    retry_rate: float
    violation_density: float
    signal_hash: str

    _FLOAT_FIELDS = ("anomaly_score", "escalation_rate", "retry_rate", "violation_density")

    def __post_init__(self) -> None:
        if self.schema_version < 1:
            raise ValueError(f"schema_version must be >= 1, got {self.schema_version}")
        if not self.mission_id:
            raise ValueError("mission_id must be non-empty")
        if self.created_at_utc < 0:
            raise ValueError(f"created_at_utc must be >= 0, got {self.created_at_utc}")
        for field_name in self._FLOAT_FIELDS:
            v = getattr(self, field_name)
            if not (0.0 <= v <= 1.0):
                raise ValueError(f"{field_name} must be in [0.0, 1.0], got {v}")
        if len(self.signal_hash) != 64:
            raise ValueError(f"signal_hash must be 64 hex chars, got len={len(self.signal_hash)}")

    def canonical_bytes(self) -> bytes:
        """Deterministic serialization excluding signal_hash (used to compute it)."""
        doc = {
            "anomaly_score": self.anomaly_score,
            "created_at_utc": self.created_at_utc,
            "escalation_rate": self.escalation_rate,
            "mission_id": self.mission_id,
            "retry_rate": self.retry_rate,
            "schema_version": self.schema_version,
            "violation_density": self.violation_density,
        }
        return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()

    @staticmethod
    def compute_hash(
        schema_version: int,
        mission_id: str,
        created_at_utc: int,
        anomaly_score: float,
        escalation_rate: float,
        retry_rate: float,
        violation_density: float,
    ) -> str:
        """Compute signal_hash from raw field values (before construction)."""
        doc = {
            "anomaly_score": anomaly_score,
            "created_at_utc": created_at_utc,
            "escalation_rate": escalation_rate,
            "mission_id": mission_id,
            "retry_rate": retry_rate,
            "schema_version": schema_version,
            "violation_density": violation_density,
        }
        raw = json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()
        return _sha256(raw)

    @classmethod
    def build(
        cls,
        mission_id: str,
        created_at_utc: int,
        anomaly_score: float,
        escalation_rate: float,
        retry_rate: float,
        violation_density: float,
        schema_version: int = 1,
    ) -> DetectionSignal:
        """Factory: compute signal_hash automatically."""
        h = cls.compute_hash(
            schema_version=schema_version,
            mission_id=mission_id,
            created_at_utc=created_at_utc,
            anomaly_score=anomaly_score,
            escalation_rate=escalation_rate,
            retry_rate=retry_rate,
            violation_density=violation_density,
        )
        return cls(
            schema_version=schema_version,
            mission_id=mission_id,
            created_at_utc=created_at_utc,
            anomaly_score=anomaly_score,
            escalation_rate=escalation_rate,
            retry_rate=retry_rate,
            violation_density=violation_density,
            signal_hash=h,
        )
