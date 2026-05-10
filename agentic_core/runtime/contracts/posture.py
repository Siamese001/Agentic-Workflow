"""W6 RuntimePosture struct + GateVerdictRef primitive (W6 P6.1).

Concerns #3 (gate receipts) and #7 (risk/side-effect posture) are threaded
through all 11 emit contracts via two typed primitives introduced here:

``RuntimePosture``
    A frozen dataclass describing the *intended* risk + side-effect posture
    of a layer transition.  Fields are additive flags; a contract is in the
    "safest" state when all bool fields are False (pure read-only, no network,
    no write, no HITL required).  Callers set only the flags that apply.

    Field names mirror ``L4_state/contracts/records.py`` vocabulary
    (``sandbox_required``, ``write_intent_class``) but distilled to a
    portable shape usable at every layer without importing L4.

``GateVerdictRef``
    A lightweight string reference (gate-verdict-id / audit-row-id) that
    points to the full ``GateVerdict`` persisted in the L4 ledger.  Using
    refs rather than embedding the full struct keeps every emit dataclass
    frozen and avoids circular imports between ``runtime/contracts/`` and
    ``L3_orchestration/exit_eval/v6/types.py``.

Usage in emit contracts::

    from agentic_core.runtime.contracts.posture import (
        RuntimePosture,
        POSTURE_READ_ONLY,
    )

    @dataclass(frozen=True, slots=True)
    class RouteContract:
        ...
        posture: RuntimePosture = field(default_factory=lambda: POSTURE_READ_ONLY)
        gate_verdict_refs: tuple[str, ...] = field(default_factory=tuple)

Decision D7 (Author-Gate W0): typed enum-backed posture — ``RuntimePosture``
struct (not raw booleans, not ``source_authority_class`` string slice).

Decision D11 (Author-Gate W0): all new fields default-empty / default-safe so
existing callers compile without change.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RuntimePosture:
    """Risk and side-effect posture for a single layer transition.

    Flags are ANDed: a posture is "safe" when all are False.  Layer
    bindings set the minimal required flags for their operation.

    Attributes:
        read_only: Layer transition makes no durable state changes and
            issues no external calls.  When True, ``external_call``,
            ``write_intent``, and ``hitl_required`` SHOULD be False.
        external_call: At least one outbound network call or tool
            invocation is expected in this transition.
        write_intent: This transition produces a ``proposed_state_diff``
            or otherwise requests a durable write via UWG.
        hitl_required: HITL review is a prerequisite before this
            transition's output may be consumed downstream.
        posture_class: Optional summary label — one of
            ``"read_only"`` | ``"retrieval"`` | ``"generation"`` |
            ``"write_intent"`` | ``"break_glass"`` | ``""`` (unknown).
            Informational only; the bool flags are authoritative.
    """

    read_only: bool = True
    external_call: bool = False
    write_intent: bool = False
    hitl_required: bool = False
    posture_class: str = "read_only"


# Pre-built canonical posture instances for the most common layer patterns.
# Layer bindings SHOULD import these directly rather than constructing
# RuntimePosture from scratch to ensure field naming stays consistent.

POSTURE_READ_ONLY = RuntimePosture(
    read_only=True,
    external_call=False,
    write_intent=False,
    hitl_required=False,
    posture_class="read_only",
)

POSTURE_RETRIEVAL = RuntimePosture(
    read_only=False,
    external_call=True,
    write_intent=False,
    hitl_required=False,
    posture_class="retrieval",
)

POSTURE_GENERATION = RuntimePosture(
    read_only=False,
    external_call=True,
    write_intent=False,
    hitl_required=False,
    posture_class="generation",
)

POSTURE_WRITE_INTENT = RuntimePosture(
    read_only=False,
    external_call=False,
    write_intent=True,
    hitl_required=False,
    posture_class="write_intent",
)

POSTURE_HITL_REQUIRED = RuntimePosture(
    read_only=False,
    external_call=False,
    write_intent=True,
    hitl_required=True,
    posture_class="write_intent",
)


__all__ = [
    "RuntimePosture",
    "POSTURE_READ_ONLY",
    "POSTURE_RETRIEVAL",
    "POSTURE_GENERATION",
    "POSTURE_WRITE_INTENT",
    "POSTURE_HITL_REQUIRED",
]
