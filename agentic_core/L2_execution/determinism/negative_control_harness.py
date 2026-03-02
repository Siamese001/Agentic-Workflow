"""NegativeControlHarness — L2 Execution determinism.

Provides a controlled tamper mechanism for proving that the determinism
digest is sensitive to configuration changes.  When the environment variable
W_HARDEN_NEGCTRL_TAMPER=1 is set, the harness injects known-bad values into
the config surface so the resulting digest MUST differ from the clean run.

Contract:
- get_config_surface()  -> dict.  Tampered if W_HARDEN_NEGCTRL_TAMPER=1.
- is_tamper_active()    -> bool.
- assert_digest_differs(clean, tampered) -> raises if they are equal.

Design invariants:
  - Only '1' triggers tampering (not 'true', 'yes', etc.).
  - Tampered surface is fully deterministic (same inputs -> same output).
  - No wall-clock access.
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any


# ---------------------------------------------------------------------------
# Tamper detection
# ---------------------------------------------------------------------------

def is_tamper_active() -> bool:
    """Return True iff W_HARDEN_NEGCTRL_TAMPER == '1' in the environment."""
    return os.environ.get("W_HARDEN_NEGCTRL_TAMPER") == "1"


# ---------------------------------------------------------------------------
# Config surface
# ---------------------------------------------------------------------------

_CLEAN_CONFIG: dict[str, Any] = {
    "blas_eps": 1e-12,
    "cutoff": 0.0,
    "decision_delta_limit": 0.1,
    "embedding_batch": 500,
    "embedding_enabled": True,
    "embedding_retry": 8,
    "max_k": 20,
    "meta_learning_enabled": True,
    "model_version": "multilingual-e5-large",
    "oscillation_detector_enabled": True,
    "proposal_only": True,
    "rlhf_delta_max": 2.0,
    "rlhf_delta_min": 0.1,
    "threads": 4,
    "top_k": 20,
}

_TAMPER_OVERRIDES: dict[str, Any] = {
    "cutoff": 0.999,
    "tampered": True,
    "top_k": 999,
}


def get_config_surface() -> dict[str, Any]:
    """Return the embedding/meta-learning config surface.

    If W_HARDEN_NEGCTRL_TAMPER=1 the surface is modified with known-bad
    values so the resulting digest differs from the clean run.
    """
    surface = dict(_CLEAN_CONFIG)
    if is_tamper_active():
        surface.update(_TAMPER_OVERRIDES)
    return surface


def hash_config_surface(surface: dict[str, Any]) -> str:
    """Return SHA-256 hex of the canonical config surface dict."""
    canonical = _canonical_json_bytes(surface)
    return hashlib.sha256(canonical).hexdigest()


# ---------------------------------------------------------------------------
# Assertion helpers
# ---------------------------------------------------------------------------

def assert_digest_differs(clean_digest: str, tampered_digest: str) -> None:
    """Assert that *clean_digest* != *tampered_digest*.

    Raises:
        AssertionError: if the two digests are identical (tamper not detected).
    """
    if clean_digest == tampered_digest:
        raise AssertionError(
            "NegativeControlHarness: digests are identical — tampering was "
            "NOT detected by the digest surface. This is a security failure.\n"
            f"  clean    = {clean_digest}\n"
            f"  tampered = {tampered_digest}"
        )


def assert_digest_stable(digest1: str, digest2: str) -> None:
    """Assert that *digest1* == *digest2* (two independent clean runs).

    Raises:
        AssertionError: if the two digests differ (non-determinism detected).
    """
    if digest1 != digest2:
        raise AssertionError(
            "NegativeControlHarness: digests differ across runs — "
            "non-determinism detected.\n"
            f"  run1 = {digest1}\n"
            f"  run2 = {digest2}"
        )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _canonical_json_bytes(data: Any) -> bytes:
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


__all__ = [
    "assert_digest_differs",
    "assert_digest_stable",
    "get_config_surface",
    "hash_config_surface",
    "is_tamper_active",
]
