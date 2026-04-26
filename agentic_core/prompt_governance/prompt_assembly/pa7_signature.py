"""PA.7 Signature Rule + canonical manifest bytes (spec lines 1405-1531).

Builds the deterministic byte representation used to:

  * compute manifest_hash (SHA-256 over canonical JSON of all input fields)
  * compute the HMAC signature using a caller-provided secret key
  * derive the replay_key (manifest_hash + idempotency_nonce composite)

The output is a :class:`SignedManifest` and a helper :func:`verify_signature`
for round-trip validation.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from typing import Any, Mapping

SIGNATURE_VERSION: str = "PA7-HMAC-SHA256-v1"


@dataclass(frozen=True)
class SignedManifest:
    """Spec PA.7 signed-manifest literal."""

    canonical_bytes: bytes
    manifest_hash: str
    signature: str
    signature_version: str
    replay_key: str
    signing_key_reference: str


def canonicalize_manifest(manifest_inputs: Mapping[str, Any]) -> bytes:
    """Convert the manifest input dict to canonical JSON bytes.

    Determinism rules:

      * sort_keys=True     -> stable key order
      * separators=(',', ':') -> no whitespace
      * ensure_ascii=False -> preserve unicode without escaping
      * default=str        -> non-JSON types get string-coerced
    """
    return json.dumps(
        manifest_inputs,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    ).encode("utf-8")


def compute_manifest_hash(canonical_bytes: bytes) -> str:
    return hashlib.sha256(canonical_bytes).hexdigest()


def compute_replay_key(manifest_hash: str, idempotency_nonce: str) -> str:
    base = manifest_hash + ":" + (idempotency_nonce or "")
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def sign_manifest(
    manifest_inputs: Mapping[str, Any],
    *,
    secret_key: bytes,
    idempotency_nonce: str = "",
    signing_key_reference: str = "",
) -> SignedManifest:
    """Compute canonical bytes, hash, signature, and replay key."""
    cb = canonicalize_manifest(manifest_inputs)
    mh = compute_manifest_hash(cb)
    sig = hmac.new(secret_key, cb, hashlib.sha256).hexdigest()
    rk = compute_replay_key(mh, idempotency_nonce)
    return SignedManifest(
        canonical_bytes=cb,
        manifest_hash=mh,
        signature=sig,
        signature_version=SIGNATURE_VERSION,
        replay_key=rk,
        signing_key_reference=signing_key_reference,
    )


def verify_signature(
    canonical_bytes: bytes,
    signature_hex: str,
    *,
    secret_key: bytes,
) -> bool:
    """Constant-time signature verification."""
    try:
        expected = hmac.new(secret_key, canonical_bytes, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature_hex)
    except (TypeError, ValueError):
        return False


__all__ = [
    "SIGNATURE_VERSION",
    "SignedManifest",
    "canonicalize_manifest",
    "compute_manifest_hash",
    "compute_replay_key",
    "sign_manifest",
    "verify_signature",
]
