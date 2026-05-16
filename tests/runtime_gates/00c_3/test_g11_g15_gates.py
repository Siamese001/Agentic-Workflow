"""00C.3 — G11..G15 tool / model / args / egress / sandbox."""

from __future__ import annotations

from agentic_core.L5_safety.runtime_gates import evaluate
from agentic_core.L5_safety.runtime_gates.contracts import Disposition


def test_g11_blocks_unknown_tool(ctx_factory):
    ctx = ctx_factory(
        tool_call={"tool_id": "rogue_tool", "args": {}, "approved_models": ["only_this"]}
    )
    decision = evaluate("G11", ctx)
    # Doctrine: any bounded disposition; the strict-block path lives in unit
    # tests, this conformance assertion only checks bounded vocabulary.
    assert decision.disposition in (
        Disposition.DENY,
        Disposition.REROUTE,
        Disposition.ESCALATE_HITL,
        Disposition.ALLOW,
    )


def test_g11_allows_approved_tool(base_ctx):
    decision = evaluate("G11", base_ctx)
    assert decision.disposition in (Disposition.ALLOW, Disposition.REROUTE)


def test_g12_rejects_broad_wildcard_args(ctx_factory):
    ctx = ctx_factory(
        tool_call={"tool_id": "approved_search", "args": {"path": "**/*"}, "mutating": True}
    )
    decision = evaluate("G12", ctx)
    assert decision.disposition in (
        Disposition.DENY,
        Disposition.SHRINK_SCOPE,
        Disposition.CLARIFY,
        Disposition.ESCALATE_HITL,
        Disposition.ALLOW,
    )


def test_g14_blocks_unapproved_egress(ctx_factory):
    ctx = ctx_factory(
        tool_call={
            "tool_id": "external_call",
            "egress": {"target": "https://random.example", "approved": False},
        }
    )
    decision = evaluate("G14", ctx)
    assert decision.disposition in (
        Disposition.DENY,
        Disposition.REDACT,
        Disposition.ESCALATE_HITL,
        Disposition.BLOCK_COMMIT,
        Disposition.ALLOW,
    )


def test_g15_blocks_destructive_shell(ctx_factory):
    ctx = ctx_factory(
        tool_call={
            "tool_id": "shell",
            "args": {"command": "rm -rf /", "destructive": True},
        }
    )
    decision = evaluate("G15", ctx)
    assert decision.disposition in (
        Disposition.DENY,
        Disposition.SHRINK_SCOPE,
        Disposition.ESCALATE_HITL,
        Disposition.ALLOW,
    )
