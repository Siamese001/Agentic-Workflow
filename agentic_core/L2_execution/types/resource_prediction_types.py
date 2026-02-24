"""
Resource prediction types for L2 execution learning.
Deterministic, frozen dataclasses with canonical serialization.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass


@dataclass(frozen=True)
class FailureSignature:
    """Deterministic signature of a failure for resource prediction."""

    component: str
    failure_type: str
    fingerprint: str  # Stable 64-hex string derived from failure context

    def canonical_bytes(self) -> bytes:
        """Canonical byte representation for hashing."""
        # Sort keys and use fixed formatting for determinism
        data = {
            "component": self.component,
            "failure_type": self.failure_type,
            "fingerprint": self.fingerprint,
        }
        # Use separators and ensure ASCII output
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
        data = {
            "cpu_cores": self.cpu_cores,
            "memory_mb": self.memory_mb,
            "timeout_s": self.timeout_s,
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")

    def content_hash(self) -> str:
        """SHA256 hex hash of canonical representation."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True)
class ResourcePrediction:
    """Deterministic resource prediction for a failure signature."""

    signature: FailureSignature
    envelope: ResourceEnvelope
    confidence: float  # 0.0 to 1.0
    reasons: tuple[str, ...]  # Deterministic reasoning

    def canonical_bytes(self) -> bytes:
        """Canonical byte representation for hashing."""
        # Round confidence to 6 decimals for stable representation
        data = {
            "signature": self.signature.canonical_bytes().decode("ascii"),
            "envelope": self.envelope.canonical_bytes().decode("ascii"),
            "confidence": round(self.confidence, 6),
            "reasons": tuple(sorted(self.reasons)),  # Sort for determinism
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("ascii")

    def content_hash(self) -> str:
        """SHA256 hex hash of canonical representation."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()
