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


class NonCanonicalManifestError(TypeError):
    """Raised when a manifest contains a non-deterministically-serializable
    type. Canonical signing requires set-free, datetime-free, callable-free
    inputs because such types either have undefined iteration order or
    string representations that drift between Python versions and locales.
    """


_CANONICAL_TYPES: tuple[type, ...] = (str, int, float, bool, type(None))


@dataclass(frozen=True)
class SignedManifest:
    """Spec PA.7 signed-manifest literal."""

    canonical_bytes: bytes
    manifest_hash: str
    signature: str
    signature_version: str
    replay_key: str
    signing_key_reference: str


_CANONICAL_SCALARS: tuple[type, ...] = (str, int, float, type(None))


def _validate_canonical(value: Any, path: str = "$") -> Any:
    """Walk the value tree, rejecting types whose JSON encoding is not
    deterministic, and converting tuples -> lists for clean json.dumps.

    Forbidden types:
      * set / frozenset       (iteration order undefined)
      * bytes / bytearray     (encoding ambiguity)
      * any callable          (repr is unstable across runs)
      * any object whose class is outside the canonical scalar / Mapping /
        list / tuple / None universe

    Allowed types: str, int, float (incl bool), None, Mapping, list, tuple.
    """
    # bool is a subclass of int; accept either as a canonical scalar.
    if isinstance(value, bool) or isinstance(value, _CANONICAL_SCALARS):
        return value
    if isinstance(value, (bytes, bytearray)):
        raise NonCanonicalManifestError(
            f"non-canonical bytes/bytearray at {path}; encode as a string upstream"
        )
    if isinstance(value, (set, frozenset)):
        raise NonCanonicalManifestError(
            f"non-canonical set at {path}; sets have no stable order — pass a sorted list"
        )
    if callable(value):
        raise NonCanonicalManifestError(f"non-canonical callable at {path}; callables are not serializable")
    if isinstance(value, Mapping):
        out: dict[str, Any] = {}
        for k, v in value.items():
            if not isinstance(k, str):
                raise NonCanonicalManifestError(f"non-string mapping key at {path}: {type(k).__name__}")
            out[k] = _validate_canonical(v, f"{path}.{k}")
        return out
    if isinstance(value, (list, tuple)):
        return [_validate_canonical(v, f"{path}[{i}]") for i, v in enumerate(value)]
    raise NonCanonicalManifestError(f"non-canonical value of type {type(value).__name__} at {path}")


def canonicalize_manifest(manifest_inputs: Mapping[str, Any]) -> bytes:
    """Convert the manifest input dict to canonical JSON bytes.

    Determinism rules:

      * sort_keys=True     -> stable key order
      * separators=(',', ':') -> no whitespace
      * ensure_ascii=False -> preserve unicode without escaping
      * Tuples normalize to lists (B6 hardening — both serialize identically)

    Raises :class:`NonCanonicalManifestError` for any non-deterministic type
    (sets, bytes, callables, non-string mapping keys, custom objects).
    """
    safe = _validate_canonical(manifest_inputs)
    return json.dumps(
        safe,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
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
    """Constant-time signature verification.

    Defensive: if either argument is the wrong type or the comparison itself
    raises, return False rather than propagating. This keeps the signature
    contract a clean boolean for callers in the hot path.
    """
    if not isinstance(signature_hex, str) or not isinstance(canonical_bytes, (bytes, bytearray)):
        return False
    try:
        expected = hmac.new(secret_key, canonical_bytes, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature_hex)
    except (TypeError, ValueError):
        return False


__all__ = [
    "SIGNATURE_VERSION",
    "NonCanonicalManifestError",
    "SignedManifest",
    "canonicalize_manifest",
    "compute_manifest_hash",
    "compute_replay_key",
    "sign_manifest",
    "verify_signature",
]
