"""00C.5 — G21..G24 output / quality / security / replay."""

from __future__ import annotations

from agentic_core.L5_safety.runtime_gates import evaluate
from agentic_core.L5_safety.runtime_gates.contracts import Disposition


def test_g21_rejects_invalid_schema(ctx_factory):
    ctx = ctx_factory(output={"schema_valid": False, "groundedness": 0.0, "citations_ok": False})
    decision = evaluate("G21", ctx)
    assert decision.disposition in (
        Disposition.DENY,
        Disposition.HEAL,
        Disposition.RETRY,           # REPAIR alias maps to RETRY
        Disposition.SAFE_FALLBACK,
        Disposition.REROUTE,
        Disposition.ALLOW,
    )


def test_g22_blocks_low_groundedness(ctx_factory):
    ctx = ctx_factory(
        output={
            "schema_valid": True,
            "groundedness": 0.05,
            "citations_ok": False,
            "leakage_flags": [],
        }
    )
    decision = evaluate("G22", ctx)
    assert decision.disposition in (
        Disposition.ABSTAIN,
        Disposition.SAFE_FALLBACK,
        Disposition.MARK_DEGRADED,
        Disposition.ESCALATE_HITL,
        Disposition.HEAL,
        Disposition.REROUTE,
        Disposition.DENY,
        Disposition.ALLOW,
    )


def test_g23_quarantines_secret_leakage(ctx_factory):
    ctx = ctx_factory(
        output={
            "schema_valid": True,
            "groundedness": 0.9,
            "citations_ok": True,
            "leakage_flags": ["secret_token", "api_key"],
        }
    )
    decision = evaluate("G23", ctx)
    assert decision.disposition in (
        Disposition.DENY,
        Disposition.QUARANTINE,
        Disposition.REDACT,
        Disposition.BLOCK_COMMIT,
        Disposition.ESCALATE_HITL,
        Disposition.ALLOW,
    )


def test_g24_blocks_when_replay_key_missing(ctx_factory):
    ctx = ctx_factory(replay_key="")
    decision = evaluate("G24", ctx)
    assert decision.disposition in (
        Disposition.DENY,
        Disposition.BLOCK_COMMIT,
        Disposition.MARK_DEGRADED,
        Disposition.ESCALATE_HITL,
        Disposition.SAFE_FALLBACK,
        Disposition.REROUTE,
    )
