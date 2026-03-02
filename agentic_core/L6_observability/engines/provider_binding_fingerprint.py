"""ProviderBindingFingerprint — L6 Observability.

Captures the provider-model binding configuration at runtime and hashes it
into a stable 64-char fingerprint for inclusion in the determinism digest
surface.

No wall-clock, no random inputs.  Provider registry is declared as a frozen
dict of (provider_id -> model_id) pairs.  Additional overrides may be passed
per-call but must be fully deterministic.

Layer rule: L6 observes only.  This module NEVER mutates routing decisions.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Canonical provider registry (structural constants, not env-driven)
# ---------------------------------------------------------------------------

_CANONICAL_PROVIDERS: dict[str, str] = {
    "anthropic": "claude-3-5-sonnet",
    "deterministic": "LOCAL_AGENT",
    "gemini": "gemini-2.5-pro",
    "openai": "gpt-4o",
    "qwen": "Qwen2.5-14B-Instruct-AWQ",
}


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ProviderBinding:
    """A single provider-model binding entry."""

    provider_id: str
    model_id: str
    tier: str


@dataclass(frozen=True)
class ProviderBindingFingerprint:
    """Immutable snapshot of all provider-model bindings + their digest."""

    bindings: tuple[ProviderBinding, ...]
    fingerprint: str

    def __post_init__(self) -> None:
        if not isinstance(self.fingerprint, str) or len(self.fingerprint) != 64:
            raise ValueError(
                f"ProviderBindingFingerprint: fingerprint must be 64-char hex"
                f", got {self.fingerprint!r}"
            )


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

def capture_provider_bindings(
    overrides: dict[str, str] | None = None,
) -> ProviderBindingFingerprint:
    """Capture current provider-model bindings and compute their fingerprint.

    Args:
        overrides: Optional dict of {provider_id: model_id} to override
            the canonical registry.  Must be deterministic (no random values).

    Returns:
        ProviderBindingFingerprint with a stable 64-char SHA-256 digest.
    """
    registry = dict(_CANONICAL_PROVIDERS)
    if overrides:
        for pid, mid in sorted(overrides.items()):
            registry[pid] = mid

    tier_map = {
        "deterministic": "DETERMINISTIC",
        "qwen": "QWEN",
        "gemini": "GEMINI",
        "anthropic": "LLM_API",
        "openai": "LLM_API",
    }

    bindings = tuple(
        ProviderBinding(
            provider_id=pid,
            model_id=mid,
            tier=tier_map.get(pid, "UNKNOWN"),
        )
        for pid, mid in sorted(registry.items())
    )

    material = {
        "bindings": [
            {"model_id": b.model_id, "provider_id": b.provider_id, "tier": b.tier}
            for b in bindings
        ]
    }
    fingerprint = hashlib.sha256(
        _canonical_json_bytes(material)
    ).hexdigest()

    return ProviderBindingFingerprint(bindings=bindings, fingerprint=fingerprint)


def fingerprint_matches(
    fp1: ProviderBindingFingerprint,
    fp2: ProviderBindingFingerprint,
) -> bool:
    """Return True if two fingerprints represent identical bindings."""
    return fp1.fingerprint == fp2.fingerprint


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
    "ProviderBinding",
    "ProviderBindingFingerprint",
    "capture_provider_bindings",
    "fingerprint_matches",
]
