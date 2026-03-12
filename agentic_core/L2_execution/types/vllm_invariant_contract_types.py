"""
PHASE 5 — Formal Invariant Verifier: Runtime Enforcement Contract.

Pure-L2 invariant contract defining architectural invariants enforced at the
execution boundary (Phase 3 adapter/controller seam).

All violations are deterministically serializable with canonical JSON and SHA256 hashing.
No GPU libraries. No torch/vllm imports. L2 purity preserved.
"""
from __future__ import annotations
import json
from dataclasses import dataclass
from enum import Enum
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class InvariantId(str, Enum):
    """Stable invariant identifiers for runtime enforcement."""
    INV_NO_GPU_IMPORTS_IN_L0_L6 = 'INV_NO_GPU_IMPORTS_IN_L0_L6'
    INV_LOCAL_REQUEST_HAS_EXPLICIT_MAX_TOKENS = 'INV_LOCAL_REQUEST_HAS_EXPLICIT_MAX_TOKENS'
    INV_LOCAL_REQUEST_TEMPERATURE_ZERO = 'INV_LOCAL_REQUEST_TEMPERATURE_ZERO'
    INV_LOCAL_REQUEST_SEED_PRESENT = 'INV_LOCAL_REQUEST_SEED_PRESENT'
    INV_TELEMETRY_HAS_FINGERPRINT_HASH = 'INV_TELEMETRY_HAS_FINGERPRINT_HASH'
    INV_REPLAY_HASH_PRESENT_WHEN_ENABLED = 'INV_REPLAY_HASH_PRESENT_WHEN_ENABLED'
    INV_GEMINI_FALLBACK_REQUIRES_REASON = 'INV_GEMINI_FALLBACK_REQUIRES_REASON'

class InvariantSeverity(str, Enum):
    """Severity levels for invariant violations."""
    INFO = 'INFO'
    WARN = 'WARN'
    FAIL = 'FAIL'

@dataclass(frozen=True)
class InvariantViolation:
    """Immutable invariant violation artifact with deterministic serialization.

    All fields are deterministic (no timestamps, no nondeterministic runtime state).
    Context dict is canonicalized with sorted keys for stable hashing.
    """
    invariant_id: str
    severity: str
    message: str
    context: dict[str, Any]

    def canonical_json(self) -> str:
        """Returns canonical JSON representation with sorted keys."""
        data = {'invariant_id': self.invariant_id, 'severity': self.severity, 'message': self.message, 'context': self.context}
        return json.dumps(data, sort_keys=True, separators=(',', ':'))

    def violation_hash(self) -> str:
        """Returns SHA256 hash of canonical JSON representation."""
        import hashlib
        return hashlib.sha256(self.canonical_json().encode('utf-8')).hexdigest()

    def as_dict(self) -> dict[str, Any]:
        """Returns dict representation with stable key ordering."""
        return {'invariant_id': self.invariant_id, 'severity': self.severity, 'message': self.message, 'context': self.context, 'violation_hash': self.violation_hash()}
