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
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace, _emit_signs_execution_trace


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
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "DigestCalculator.compute")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:DigestCalculator.compute".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
