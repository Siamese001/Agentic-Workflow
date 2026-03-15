"""Arbitration types for deterministic multi-agent proposal selection."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


@dataclass(frozen=True)
class ArbitrationCandidate:
    """A candidate proposal for arbitration."""

    id: str
    kind: str
    payload: dict[str, Any]
    score: float
    cost: float
    provenance: str
    created_at: int | None = None

    def canonical_bytes(self) -> bytes:
        """Canonical byte representation for deterministic fingerprinting."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ArbitrationCandidate.canonical_bytes")

        data = {
            "id": self.id,
            "kind": self.kind,
            "payload": self.payload,
            "score": self.score,
            "cost": self.cost,
            "provenance": self.provenance,
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")


@dataclass(frozen=True)
class ArbitrationPolicy:
    """Policy governing arbitration decisions."""

    weights: dict[str, float]
    caps: dict[str, Any]
    thresholds: dict[str, float]
    allowed_kinds: set[str]

    def canonical_bytes(self) -> bytes:
        """Canonical byte representation for deterministic fingerprinting."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ArbitrationPolicy.canonical_bytes")

        data = {
            "weights": self.weights,
            "caps": self.caps,
            "thresholds": self.thresholds,
            "allowed_kinds": sorted(self.allowed_kinds),
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")


@dataclass(frozen=True)
class ArbitrationDecision:
    """Result of arbitration process."""

    winner_ids: tuple[str, ...]
    merged_payload: dict[str, Any] | None
    rationale_codes: tuple[str, ...]
    deterministic_fingerprint: str

    def canonical_bytes(self) -> bytes:
        """Canonical byte representation for deterministic fingerprinting."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ArbitrationDecision.canonical_bytes")

        data = {
            "winner_ids": self.winner_ids,
            "merged_payload": self.merged_payload,
            "rationale_codes": self.rationale_codes,
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")

    def content_hash(self) -> str:
        """SHA256 hex hash of canonical representation."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()
