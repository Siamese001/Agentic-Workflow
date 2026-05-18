"""W10 — block direct L2/L6 durable R1B writes; UWG is the only admission path."""

from __future__ import annotations

from typing import Any

from apps_rg.cache.r1b_constants import R1B_UWG_TARGET_SURFACE

FORBIDDEN_DURABLE_WRITE_SURFACES: frozenset[str] = frozenset(
    {
        "L0",
        "L1",
        "L2",
        "L3",
        "L5",
        "L6",
        "C0",
        "PromptAssembly",
        "Tool",
        "Model",
        "HITL",
    }
)

AUTHORIZED_DURABLE_WRITE_SURFACES: frozenset[str] = frozenset({"Exit", "UWG"})


def assert_r1b_durable_write_authority(*, attempting_surface: str) -> None:
    """Raise if a non-Exit surface attempts a durable R1B cache write."""
    surface = str(attempting_surface or "").strip()
    if surface in AUTHORIZED_DURABLE_WRITE_SURFACES:
        return
    if surface in FORBIDDEN_DURABLE_WRITE_SURFACES:
        raise R1BDirectDurableWriteForbidden(
            f"R1B durable cache write forbidden from {surface!r}; "
            "only Exit→UWG admission may persist durable R1B records."
        )
    raise R1BDirectDurableWriteForbidden(
        f"R1B durable cache write not authorized for surface {surface!r}."
    )


class R1BDirectDurableWriteForbidden(RuntimeError):
    """L2/L6 or other surfaces attempted to bypass UWG for R1B persistence."""


def record_blocked_direct_r1b_write(
    *,
    attempting_surface: str,
    reason: str,
    request_id: str | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Emit a UWG blocked-direct-write receipt (proof fixture helper)."""
    from agentic_core.L4_state.uwg.durable_write_gateway import DurableWriteGateway

    gw = DurableWriteGateway()
    receipt = gw.reject_direct_write(
        attempting_surface=attempting_surface,
        target_surface=R1B_UWG_TARGET_SURFACE,
        reason=reason,
        request_id=request_id,
        run_id=run_id,
    )
    return {
        "blocked_commit_receipt_id": receipt.blocked_commit_receipt_id,
        "blocked_reason_codes": list(receipt.blocked_reason_codes),
        "failed_rule_ids": list(receipt.failed_rule_ids),
        "target_surface": R1B_UWG_TARGET_SURFACE,
        "attempting_surface": attempting_surface,
    }


__all__ = [
    "AUTHORIZED_DURABLE_WRITE_SURFACES",
    "FORBIDDEN_DURABLE_WRITE_SURFACES",
    "R1BDirectDurableWriteForbidden",
    "assert_r1b_durable_write_authority",
    "record_blocked_direct_r1b_write",
]
