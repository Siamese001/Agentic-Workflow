"""Addendum 3.1: C0 Authority Leak Guard.

C0 RAG is informational only — must not carry authority fields.
Raises C0AuthorityLeakError if forbidden fields are present.
"""

from __future__ import annotations

from typing import Any


def _get_hardening_errors():
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
