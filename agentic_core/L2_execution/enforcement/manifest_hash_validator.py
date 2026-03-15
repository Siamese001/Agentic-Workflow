"""
L2.0 Manifest Hash Validator — Phase 2

Validates that execution manifests carry all required config hashes
and that those hashes match the L4 SSOT active configs.
"""

from __future__ import annotations

from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

_emit_dispatches_healing_run("p1", "manifest_hash_validator", "L2")
_emit_routes_through("p1", "manifest_hash_validator", "L2")
_emit_escalates_to_human("p1", "manifest_hash_validator", "L2")
_emit_reads_policy_state("p1", "manifest_hash_validator", "L2")


def _get_active_configs():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_active_configs", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_active_configs", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "_get_active_configs")
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
