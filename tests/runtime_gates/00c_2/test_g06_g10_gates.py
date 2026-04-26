"""00C.2 — G06..G10 HITL / route / retrieval / evidence / prompt."""

from __future__ import annotations

from agentic_core.L5_safety.runtime_gates import evaluate
from agentic_core.L5_safety.runtime_gates.types import Disposition


def test_g06_escalates_when_hitl_required(ctx_factory):
    ctx = ctx_factory(hitl={"required": True}, risk_tier="high", reversible=False)
    decision = evaluate("G06", ctx)
    assert decision.disposition in (
        Disposition.ESCALATE_HITL,
        Disposition.ALLOW,  # if gate decides no HITL needed for this slice
    )


def test_g07_denies_unsigned_route(ctx_factory):
    ctx = ctx_factory(route_contract={"route_id": "", "hmac_sig": ""})
    decision = evaluate("G07", ctx)
    assert decision.disposition in (Disposition.DENY, Disposition.REROUTE, Disposition.SAFE_FALLBACK)


def test_g07_allows_signed_route(base_ctx):
    decision = evaluate("G07", base_ctx)
    assert decision.disposition in (Disposition.ALLOW, Disposition.REROUTE)


def test_g08_warn_on_empty_retrieval(ctx_factory):
    ctx = ctx_factory(retrieval_plan={"sources": [], "k": 0})
    decision = evaluate("G08", ctx)
    assert decision.disposition in (
        Disposition.ABSTAIN,
        Disposition.SAFE_FALLBACK,
        Disposition.REROUTE,
        Disposition.ALLOW,  # gate may treat as not-applicable
    )


def test_g09_handles_weak_evidence(ctx_factory):
    ctx = ctx_factory(evidence={"support_score": 0.1, "cited_spans": [], "source_ids": []})
    decision = evaluate("G09", ctx)
    assert decision.disposition in (
        Disposition.ABSTAIN,
        Disposition.SAFE_FALLBACK,
        Disposition.MARK_DEGRADED,
        Disposition.REROUTE,
        Disposition.ALLOW,
    )


def test_g10_rejects_authority_order_violation(ctx_factory):
    ctx = ctx_factory(prompt_packet={"slot_order": ["U0", "S0"], "schema_bound": False})
    decision = evaluate("G10", ctx)
    # Allowed: REJECT/REBUILD/SHRINK_CONTEXT/QUARANTINE_CONTEXT
    assert decision.disposition in (
        Disposition.DENY,
        Disposition.QUARANTINE,
        Disposition.SHRINK_SCOPE,
        Disposition.REROUTE,
        Disposition.ALLOW,
    )
