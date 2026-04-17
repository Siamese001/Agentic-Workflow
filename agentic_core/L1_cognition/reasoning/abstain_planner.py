"""Backward-compat shim for the abstain contract.

The SSOT was promoted to ``agentic_core.runtime.contracts.abstain_contract``
so lower layers (notably L0 ``path_router``) can consume the primitive
without triggering a layer-gravity violation. This module re-exports every
previously-public name to preserve import paths used by L3 consumers and
existing tests.

New callers should import from the contract module directly:

    from agentic_core.runtime.contracts.abstain_contract import plan_abstain
"""

from __future__ import annotations

from agentic_core.runtime.contracts.abstain_contract import (
    ACTION_CONTINUE,
    ACTION_EMIT_R5,
    DECISION_ABSTAIN,
    DECISION_PROCEED,
    DEFAULT_ABSTAIN_THRESHOLD,
    AbstainDecision,
    plan_abstain,
)

__all__ = [
    "ACTION_CONTINUE",
    "ACTION_EMIT_R5",
    "AbstainDecision",
    "DECISION_ABSTAIN",
    "DECISION_PROCEED",
    "DEFAULT_ABSTAIN_THRESHOLD",
    "plan_abstain",
]
