"""
agentic_core/interfaces/determinism.py

L0-centralized determinism interface for apps_* consumption.

AUTHORITY CONSTRAINTS:
- All canonicalization delegates to L0 assembly_stage.canonical_bytes
- No local canonicalization logic — prevents replay integrity divergence
- Read-only operations only — no state mutation
- JSON-serializable inputs enforced

USAGE (apps_*):
    from agentic_core.interfaces.determinism import (
        canonical_bytes,
        canonical_hash,
        strip_nondeterministic,
        DETERMINISM_EXCLUDED_FIELDS,
    )
"""

from __future__ import annotations

import hashlib
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "determinism")
_emit_applies_guardrail("p0", "determinism", "p0_governance")
_emit_reads_policy_state("p0", "determinism", "policy_binding")
_emit_snapshots_state("p0", "determinism", "state_snapshot")
emit_replay_key("p0", "determinism")
emit_determinism_digest("p0", "determinism")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

DETERMINISM_EXCLUDED_FIELDS: frozenset[str] = frozenset(
    {"duration_ms", "timestamp", "trace_id", "cycle_counter", "telemetry", "created_at", "updated_at"}
)


def canonical_bytes(data: dict[str, Any]) -> bytes:
    """
    Proxy to L0 assembly_stage.canonical_bytes.

    Centralizes canonicalization — no local logic duplication.
    Prevents replay integrity breaks across layers.
    """
    from agentic_core.L0_routing.engines.assembly_stage import canonical_bytes as _l0_canonical_bytes

    return _l0_canonical_bytes(data)


def canonical_hash(data: dict[str, Any]) -> str:
    """
    Return hex SHA-256 of the canonical bytes.

    Delegates to L0 canonical_bytes — no independent logic.
    """
    return hashlib.sha256(canonical_bytes(data)).hexdigest()


def strip_nondeterministic(
    data: dict[str, Any], excluded_fields: frozenset[str] | None = None
) -> dict[str, Any]:
    """
    Return a copy of data with nondeterministic fields removed.

    Read-only — never mutates the caller-owned dict.
    """
    excluded = excluded_fields if excluded_fields is not None else DETERMINISM_EXCLUDED_FIELDS
    return {k: v for k, v in data.items() if k not in excluded}


__all__ = ["canonical_bytes", "canonical_hash", "strip_nondeterministic", "DETERMINISM_EXCLUDED_FIELDS"]
