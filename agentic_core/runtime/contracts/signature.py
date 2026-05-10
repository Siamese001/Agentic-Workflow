"""HMAC-SHA256 signature helper for W6 emit contracts (W5 P5.2).

Pattern borrowed from ``L0RouteContract.hmac_sig`` — the ``hmac_sig``
field on that contract is already validated by callers.  This module
provides the shared compute/verify helpers so every emit contract can
produce a self-authenticating ``signature`` field using the same
algorithm.

Decision D9 (Author-Gate W0): HMAC-SHA256, per-layer-issued (not a
chain signature), key sourced from environment or caller-supplied key.

Usage::

    from agentic_core.runtime.contracts.signature import compute_contract_hmac
    sig = compute_contract_hmac(payload_bytes, key=signing_key)

The ``signature`` field on each emit dataclass defaults to ``""``
(unsigned).  Callers that have a key SHOULD compute and set it.
Verifiers that have the key SHOULD call ``verify_contract_hmac``.
Verifiers that lack the key MUST treat an empty signature as
``UNVERIFIED`` (not ``INVALID``) — fail-soft per D5.
"""

from __future__ import annotations

import hashlib
import hmac
import os

# Default env variable that holds the HMAC key bytes (hex-encoded).
_HMAC_KEY_ENV = "W6_CONTRACT_HMAC_KEY"

# Sentinel returned by verify when no key is available.
UNVERIFIED = "UNVERIFIED"


def _resolve_key(key: bytes | str | None) -> bytes | None:
    """Resolve signing key: caller-supplied > env var > None (unsigned)."""
    if key is not None:
        return key if isinstance(key, bytes) else key.encode("utf-8")
    raw = os.environ.get(_HMAC_KEY_ENV, "")
    if raw:
        try:
            return bytes.fromhex(raw)
        except ValueError:
            return raw.encode("utf-8")
    return None


def compute_contract_hmac(
    payload: bytes,
    *,
    key: bytes | str | None = None,
) -> str:
    """Return HMAC-SHA256 hex digest over ``payload``, or ``""`` if no key.

    Args:
        payload: canonical serialization of the contract (e.g. JSON bytes).
        key: signing key; falls back to ``W6_CONTRACT_HMAC_KEY`` env var.

    Returns:
        Hex-encoded HMAC-SHA256 string, or empty string when no key is
        available (unsigned — fail-soft per D5).
    """
    resolved = _resolve_key(key)
    if resolved is None:
        return ""
    return hmac.new(resolved, payload, hashlib.sha256).hexdigest()


def verify_contract_hmac(
    payload: bytes,
    expected_sig: str,
    *,
    key: bytes | str | None = None,
) -> str:
    """Verify HMAC-SHA256 of ``payload`` against ``expected_sig``.

    Returns:
        ``"OK"`` — signatures match.
        ``"INVALID"`` — signatures do not match (tamper evidence).
        ``UNVERIFIED`` — no key available; cannot verify (fail-soft).
    """
    resolved = _resolve_key(key)
    if resolved is None:
        return UNVERIFIED
    if not expected_sig:
        return UNVERIFIED
    actual = hmac.new(resolved, payload, hashlib.sha256).hexdigest()
    if hmac.compare_digest(actual, expected_sig):
        return "OK"
    return "INVALID"


__all__ = [
    "UNVERIFIED",
    "compute_contract_hmac",
    "verify_contract_hmac",
]
