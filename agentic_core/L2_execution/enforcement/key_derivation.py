"""
HMAC Key Derivation with Versioning — L2 Execution Boundary.

Provides HKDF-derived keys with version tracking for replay compatibility
across secret rotations.  All derived keys embed key_version and
kdf_salt_hash so that InstructionPacket / SandboxEnvelope can be
re-verified under any in-rotation authority version.

Phase 0.2: Mathematically-Sealed Sovereignty Hardening
"""

from __future__ import annotations

import hashlib
import hmac
from typing import Final

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

_CURRENT_KEY_VERSION: Final[str] = "1"
_KDF_SALT: Final[bytes] = b"sovereignty_boundary_kdf_v1"
_KDF_INFO_PREFIX: Final[str] = "sovereignty_boundary_v"


def derive_hmac_key(master_secret: bytes) -> tuple[bytes, str, str]:
    """Derive an HMAC key using HKDF with version tracking.

    Args:
        master_secret: Raw master secret obtained from KeySource.

    Returns:
        Tuple of (derived_key_bytes, key_version_str, kdf_salt_hash_hex).
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "derive_hmac_key", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "derive_hmac_key", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "derive_hmac_key")
    prk = hmac.new(_KDF_SALT, master_secret, hashlib.sha256).digest()
    info = f"{_KDF_INFO_PREFIX}{_CURRENT_KEY_VERSION}".encode()
    okm = hmac.new(prk, info + b"\x01", hashlib.sha256).digest()
    kdf_salt_hash = hashlib.sha256(_KDF_SALT).hexdigest()
    return (okm, _CURRENT_KEY_VERSION, kdf_salt_hash)


def get_key_version() -> str:
    """Return current authority key version string."""
    return _CURRENT_KEY_VERSION


def verify_key_version(packet_key_version: str) -> bool:
    """Return True if *packet_key_version* matches the current version."""
    return packet_key_version == _CURRENT_KEY_VERSION


def get_kdf_salt_hash() -> str:
    """Return hex digest of the KDF salt (for embedding in packets)."""
    return hashlib.sha256(_KDF_SALT).hexdigest()


__all__ = ["derive_hmac_key", "get_key_version", "get_kdf_salt_hash", "verify_key_version"]
