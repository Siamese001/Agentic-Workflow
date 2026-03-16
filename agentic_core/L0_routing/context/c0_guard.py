"""Addendum 3.1: C0 Authority Leak Guard.

C0 RAG is informational only — must not carry authority fields.
Raises C0AuthorityLeakError if forbidden fields are present.
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
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "c0_guard")
emit_determinism_digest("p0", "c0_guard")

_emit_dispatches_healing_run("p1", "c0_guard", "L0")
_emit_routes_through("p1", "c0_guard", "L0")
_emit_escalates_to_human("p1", "c0_guard", "L0")
_emit_reads_policy_state("p1", "c0_guard", "L0")


def _get_hardening_errors():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_hardening_errors", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_hardening_errors", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "_get_hardening_errors")
    from agentic_core.L5_safety.types.hardening_errors import C0AuthorityLeakError, C0MutationViolation

    return C0AuthorityLeakError, C0MutationViolation


_FORBIDDEN_AUTHORITY_FIELDS = frozenset(
    {"route_mode", "execution_tier", "safety_threshold", "allowed_tools", "auth_token"}
)


def guard_c0_payload(payload: dict[str, Any]) -> None:
    """Raise C0AuthorityLeakError if payload contains authority fields.

    Wire into RAG context assembly before payload is passed downstream.
    """
    leaked = _FORBIDDEN_AUTHORITY_FIELDS & set(payload.keys())
    if leaked:
        C0AuthorityLeakError, _ = _get_hardening_errors()
        raise C0AuthorityLeakError(
            f"C0 payload contains forbidden authority fields: {sorted(leaked)}. "
            "C0 RAG context is informational only."
        )


def verify_c0_immutability(payload_pre: dict[str, Any], payload_post: dict[str, Any]) -> None:
    """Raise C0MutationViolation if the payload was modified during assembly.

    Addendum 3.2: context mutation prevention.
    """
    import hashlib  # noqa: E401 (inline import acceptable here)
    import json

    def _hash(d: dict[str, Any]) -> str:
        return hashlib.sha256(
            json.dumps(d, sort_keys=True, ensure_ascii=True, default=str).encode()
        ).hexdigest()

    if _hash(payload_pre) != _hash(payload_post):
        _, C0MutationViolation = _get_hardening_errors()
        raise C0MutationViolation("C0 context payload was mutated during assembly — hash mismatch.")


__all__ = ["guard_c0_payload", "verify_c0_immutability"]
