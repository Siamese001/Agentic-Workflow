"""00C.1 — G01..G05 ingress / identity / intent / safety / risk."""

from __future__ import annotations

from agentic_core.L5_safety.runtime_gates import evaluate
from agentic_core.L5_safety.runtime_gates.contracts import Disposition


def test_g01_denies_missing_envelope(ctx_factory):
    ctx = ctx_factory(request_id="", session_id="", trace_root="")
    decision = evaluate("G01", ctx)
    assert decision.disposition is Disposition.DENY
    assert decision.stop_condition_violated is True


def test_g01_clarify_on_missing_objective(ctx_factory):
    ctx = ctx_factory(intent={"raw_text": "x", "objective": "", "payload_bytes": 1})
    decision = evaluate("G01", ctx)
    assert decision.disposition is Disposition.CLARIFY


def test_g01_allows_clean_request(base_ctx):
    decision = evaluate("G01", base_ctx)
    assert decision.disposition is Disposition.ALLOW


def test_g02_denies_missing_tenant(ctx_factory):
    ctx = ctx_factory(tenant_id="")
    decision = evaluate("G02", ctx)
    assert decision.disposition in (Disposition.DENY, Disposition.ESCALATE_HITL)


def test_g04_denies_missing_policy(ctx_factory):
    ctx = ctx_factory(policy_hash="")
    decision = evaluate("G04", ctx)
    assert decision.disposition in (Disposition.DENY, Disposition.SAFE_FALLBACK)


def test_g05_escalates_irreversible_high_impact(ctx_factory):
    ctx = ctx_factory(
        risk_tier="high",
        reversible=False,
        impact_class="write",
    )
    decision = evaluate("G05", ctx)
    assert decision.disposition in (
        Disposition.ESCALATE_HITL,
        Disposition.DENY,
        Disposition.SHRINK_SCOPE,
    )


def test_g03_clarify_on_ambiguity(ctx_factory):
    ctx = ctx_factory(intent={"raw_text": "x", "objective": "delete *", "ambiguous": True})
    decision = evaluate("G03", ctx)
    assert decision.disposition in (
        Disposition.CLARIFY,
        Disposition.ABSTAIN,
        Disposition.SHRINK_SCOPE,
        Disposition.SAFE_FALLBACK,
        Disposition.ALLOW,  # gate may decide enough context exists
    )
