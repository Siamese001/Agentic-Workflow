"""L1-facing wrapper over the clarify contract (ADR-043 §T3 exit branches).

The SSOT primitive (``ClarifyDecision``, ``plan_clarify``, action / decision
constants) lives in :mod:`agentic_core.runtime.contracts.abstain_contract`
so L0 consumers can import it without a layer-gravity violation.  This
module is the L1-facing re-export shim, analogous to :mod:`abstain_planner`.

Callers producing L1PlanContractV2 should invoke :func:`plan_clarify` at
the T3 exit to decide whether the contract should carry
``proposed_route=ProposedRoute.CLARIFY`` or proceed with a normal route.
"""

from __future__ import annotations

from agentic_core.runtime.contracts.abstain_contract import (
    ACTION_CONTINUE,
    ACTION_REQUEST_CLARIFICATION,
    DECISION_CLARIFY,
    DECISION_PROCEED,
    DEFAULT_AMBIGUITY_THRESHOLD,
    ClarifyDecision,
    plan_clarify,
)

__all__ = [
    "ACTION_CONTINUE",
    "ACTION_REQUEST_CLARIFICATION",
    "ClarifyDecision",
    "DECISION_CLARIFY",
    "DECISION_PROCEED",
    "DEFAULT_AMBIGUITY_THRESHOLD",
    "plan_clarify",
]
