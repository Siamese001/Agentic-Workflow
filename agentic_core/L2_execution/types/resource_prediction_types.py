"""
Resource prediction types for L2 execution learning.
Deterministic, frozen dataclasses with canonical serialization.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace, _emit_signs_execution_trace


@dataclass(frozen=True)
class FailureSignature:
    """Deterministic signature of a failure for resource prediction."""

    component: str
    failure_type: str
    fingerprint: str

    def canonical_bytes(self) -> bytes:
        """Canonical byte representation for hashing."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "FailureSignature.canonical_bytes")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:FailureSignature.canonical_bytes".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        data = {
            "component": self.component,
            "failure_type": self.failure_type,
            "fingerprint": self.fingerprint,
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")

    def content_hash(self) -> str:
        """SHA256 hex hash of canonical representation."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True)
class ResourceEnvelope:
    """Bounded resource envelope for execution."""

    cpu_cores: int
    memory_mb: int
    timeout_s: int

    def canonical_bytes(self) -> bytes:
        """Canonical byte representation for hashing."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "ResourceEnvelope.canonical_bytes")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:ResourceEnvelope.canonical_bytes".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        data = {"cpu_cores": self.cpu_cores, "memory_mb": self.memory_mb, "timeout_s": self.timeout_s}
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")

    def content_hash(self) -> str:
        """SHA256 hex hash of canonical representation."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True)
class ResourcePrediction:
    """Deterministic resource prediction for a failure signature."""

    signature: FailureSignature
    envelope: ResourceEnvelope
    confidence: float
    reasons: tuple[str, ...]

    def canonical_bytes(self) -> bytes:
        """Canonical byte representation for hashing."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "ResourcePrediction.canonical_bytes")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:ResourcePrediction.canonical_bytes".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        data = {
            "signature": self.signature.canonical_bytes().decode("ascii"),
            "envelope": self.envelope.canonical_bytes().decode("ascii"),
            "confidence": round(self.confidence, 6),
            "reasons": tuple(sorted(self.reasons)),
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")

    def content_hash(self) -> str:
        """SHA256 hex hash of canonical representation."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()
