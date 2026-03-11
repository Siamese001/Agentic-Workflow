"""
DigestCalculator — Strict determinism surface for L2 execution.

Defines and computes the canonical W<n>-DETERMINISM-DIGEST.  Only the
five approved components are included:

    sha256(
        policy_hash        +
        registry_hash      +
        config_surface_hash +
        transcript_hash    +
        dependency_lock_hash
    )

Excluded (by design):
  - Environment variables
  - Wall-clock timestamps
  - Build IDs
  - Machine IDs
  - Random seeds

Phase 0.3: Mathematically-Sealed Sovereignty Hardening
"""

from __future__ import annotations

import hashlib

from agentic_core.utils.canonical_json_util import CanonicalJSON


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class DigestCalculator:
    """Compute the canonical determinism digest from its five components."""

    COMPONENT_KEYS = (
        "policy_hash",
        "registry_hash",
        "config_surface_hash",
        "transcript_hash",
        "dependency_lock_hash",
    )

    @classmethod
    def compute(
        self,
        *,
        policy_hash: str,
        registry_hash: str,
        config_surface_hash: str,
        transcript_hash: str,
        dependency_lock_hash: str,
    ) -> str:
        """Return SHA-256 hex digest of the canonical determinism surface.

        All five arguments must be 64-character lowercase hex strings (SHA-256).
        """
        for name, value in [
            ("policy_hash", policy_hash),
            ("registry_hash", registry_hash),
            ("config_surface_hash", config_surface_hash),
            ("transcript_hash", transcript_hash),
            ("dependency_lock_hash", dependency_lock_hash),
        ]:
            if not (isinstance(value, str) and len(value) == 64):
                raise ValueError(f"DigestCalculator: {name} must be a 64-char hex string, got {value!r}")

        material = {
            "config_surface_hash": config_surface_hash,
            "dependency_lock_hash": dependency_lock_hash,
            "policy_hash": policy_hash,
            "registry_hash": registry_hash,
            "transcript_hash": transcript_hash,
        }
        canonical = CanonicalJSON.serialize_bytes(material)
        return hashlib.sha256(canonical).hexdigest()

    @staticmethod
    def zero_hash() -> str:
        """Return a deterministic placeholder SHA-256 (all zeros)."""
        return "0" * 64


__all__ = ["DigestCalculator"]
