"""Failure fingerprinting types for deterministic failure clustering."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


@dataclass(frozen=True)
class FailureEvent:
    """Structured failure event for deterministic fingerprinting."""

    exc_type: str
    error_code: str
    component: str
    symbols: list[str]
    metadata: dict[str, Any]

    def canonical_bytes(self) -> bytes:
        """Canonical byte representation for deterministic fingerprinting."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "FailureEvent.canonical_bytes")

        data = {
            "exc_type": self.exc_type,
            "error_code": self.error_code,
            "component": self.component,
            "symbols": sorted(self.symbols),
            "metadata": {k: str(v) for k, v in sorted(self.metadata.items())},
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")


@dataclass(frozen=True)
class FailureFingerprint:
    """Deterministic fingerprint for failure clustering."""

    fingerprint_sha256: str
    canonical_bytes: bytes

    @classmethod
    def from_canonical_bytes(cls, canonical_bytes: bytes) -> FailureFingerprint:
        """Create fingerprint from canonical bytes."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "FailureFingerprint.from_canonical_bytes")

        fingerprint_sha256 = hashlib.sha256(canonical_bytes).hexdigest()
        return cls(fingerprint_sha256=fingerprint_sha256, canonical_bytes=canonical_bytes)
