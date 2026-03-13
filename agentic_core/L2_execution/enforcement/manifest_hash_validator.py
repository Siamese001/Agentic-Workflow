"""
L2.0 Manifest Hash Validator — Phase 2

Validates that execution manifests carry all required config hashes
and that those hashes match the L4 SSOT active configs.
"""

from __future__ import annotations

from typing import Any


def _get_active_configs():
    from agentic_core.L4_state.config.versioned_configs import get_active_configs

    return get_active_configs


REQUIRED_HASH_FIELDS = ("policy_hash", "routing_hash", "model_hash", "budget_hash")


class ManifestHashError(Exception):
    """Raised when manifest is missing or has mismatched config hashes."""

    pass


def validate_manifest_hashes(manifest: Any) -> None:
    """
    L2.0 gate: reject manifest if any required config hash is missing
    or does not match the L4 SSOT active config.

    Args:
        manifest: Any object with hash attributes, or a dict.

    Raises:
        ManifestHashError: on missing field or hash mismatch.
    """
    active = _get_active_configs()().hashes()
    for field in REQUIRED_HASH_FIELDS:
        if isinstance(manifest, dict):
            value = manifest.get(field)
        else:
            value = getattr(manifest, field, None)
        if value is None:
            raise ManifestHashError(f"Manifest missing required field: {field}")
        expected = active[field]
        if value != expected:
            raise ManifestHashError(f"Hash mismatch for {field}: manifest={value!r} vs L4_SSOT={expected!r}")
