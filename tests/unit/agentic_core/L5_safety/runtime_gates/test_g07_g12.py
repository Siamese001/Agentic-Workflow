"""Tests for runtime gates G07-G12 (W2)."""

from __future__ import annotations

from agentic_core.L5_safety.runtime_gates import (
    DecisionAlias,
    Disposition,
    GateContext,
    evaluate,
)


def _full_route() -> dict:
    return {
        "route_id": "R3_GROUNDED_READ",
        "confidence": 0.9,
        "reason_codes": ["grounding_required"],
        "freshness_class": "fresh",
        "cache_policy": "miss_on_intent_change",
        "execution_form": "answer_only",
        "cost_tier": "low",
        "fallback_chain": ["R1_SEMANTIC_CACHE"],
        "slo": "5s",
        "tenant_scope": "tenant-A",
        "hmac_sig": "sig-x",
    }


# ---- G07 Route Selection ----


def test_g07_allow_signed_route() -> None:
    ctx = GateContext(route_contract=_full_route())
    d = evaluate("G07", ctx)
    assert d.disposition is Disposition.ALLOW
    assert d.alias == DecisionAlias.ROUTE_R3_GROUNDED_READ.value


def test_g07_deny_incomplete_route() -> None:
    rc = _full_route()
    rc.pop("hmac_sig")
    ctx = GateContext(route_contract=rc)
    d = evaluate("G07", ctx)
    assert d.disposition is Disposition.DENY


def test_g07_mark_degraded_low_confidence() -> None:
    rc = _full_route()
    rc["confidence"] = 0.3
    ctx = GateContext(route_contract=rc)
    d = evaluate("G07", ctx)
    assert d.disposition is Disposition.MARK_DEGRADED


def test_g07_reroute_unknown_route_id() -> None:
    rc = _full_route()
    rc["route_id"] = "R99_FUTURE_ROUTE"
    ctx = GateContext(route_contract=rc)
    d = evaluate("G07", ctx)
    assert d.disposition is Disposition.REROUTE


# ---- G08 Retrieval Grounding ----


def test_g08_allow_no_grounding_required() -> None:
    ctx = GateContext(retrieval_plan={"grounding_required": False})
    d = evaluate("G08", ctx)
    assert d.disposition is Disposition.ALLOW


def test_g08_abstain_blocked_sources() -> None:
    ctx = GateContext(
        retrieval_plan={"grounding_required": True, "blocked_sources": True, "candidate_count": 5}
    )
    d = evaluate("G08", ctx)
    assert d.disposition is Disposition.ABSTAIN


def test_g08_abstain_empty_retrieval() -> None:
    ctx = GateContext(retrieval_plan={"grounding_required": True, "candidate_count": 0, "modes": ["dense"]})
    d = evaluate("G08", ctx)
    assert d.disposition is Disposition.ABSTAIN


def test_g08_retry_weak_support() -> None:
    ctx = GateContext(
        retrieval_plan={
            "grounding_required": True,
            "candidate_count": 3,
            "modes": ["dense"],
            "support_score": 0.2,
        }
    )
    d = evaluate("G08", ctx)
    assert d.disposition is Disposition.RETRY


def test_g08_allow_strong_retrieval() -> None:
    ctx = GateContext(
        retrieval_plan={
            "grounding_required": True,
            "candidate_count": 5,
            "modes": ["dense", "graph"],
            "support_score": 0.85,
        }
    )
    d = evaluate("G08", ctx)
    assert d.disposition is Disposition.ALLOW


# ---- G09 Evidence Quality ----


def test_g09_allow_strong_evidence() -> None:
    ctx = GateContext(
        evidence={
            "source_ids": ["s1", "s2"],
            "support_score": 0.9,
            "coverage": 0.8,
            "cited_spans": ["s1#L1-3"],
        }
    )
    d = evaluate("G09", ctx)
    assert d.disposition is Disposition.ALLOW


def test_g09_abstain_no_sources() -> None:
    ctx = GateContext(evidence={"source_ids": []})
    d = evaluate("G09", ctx)
    assert d.disposition is Disposition.ABSTAIN


def test_g09_mark_degraded_contradictions() -> None:
    ctx = GateContext(
        evidence={
            "source_ids": ["s1"],
            "contradictions": 2,
            "support_score": 0.9,
            "coverage": 0.8,
            "cited_spans": ["x"],
        }
    )
    d = evaluate("G09", ctx)
    assert d.disposition is Disposition.MARK_DEGRADED


def test_g09_retry_weak() -> None:
    ctx = GateContext(
        evidence={"source_ids": ["s1"], "support_score": 0.2, "coverage": 0.2, "cited_spans": ["x"]}
    )
    d = evaluate("G09", ctx)
    assert d.disposition is Disposition.RETRY


# ---- G10 Prompt Assembly ----


def _good_packet() -> dict:
    return {
        "slot_order": ["S0", "I0", "C0", "U0"],
        "max_tokens": 50_000,
        "used_tokens": 1_000,
        "hmac": "h1",
        "manifest_hash": "m1",
    }


def test_g10_allow_good_packet() -> None:
    ctx = GateContext(prompt_packet=_good_packet())
    d = evaluate("G10", ctx)
    assert d.disposition is Disposition.ALLOW


def test_g10_deny_authority_order_violation() -> None:
    p = _good_packet()
    p["slot_order"] = ["U0", "S0"]  # U0 before S0 = authority inversion
    ctx = GateContext(prompt_packet=p)
    d = evaluate("G10", ctx)
    assert d.disposition is Disposition.DENY
    assert d.stop_condition_violated


def test_g10_retry_token_overflow() -> None:
    p = _good_packet()
    p["used_tokens"] = 999_999
    ctx = GateContext(prompt_packet=p)
    d = evaluate("G10", ctx)
    assert d.disposition is Disposition.RETRY


def test_g10_deny_unsigned_packet() -> None:
    p = _good_packet()
    p.pop("hmac")
    ctx = GateContext(prompt_packet=p)
    d = evaluate("G10", ctx)
    assert d.disposition is Disposition.DENY


# ---- G11 Tool/Model Registry ----


def test_g11_allow_approved_tool() -> None:
    ctx = GateContext(
        tool_call={
            "tool_id": "search",
            "model_id": "gpt-4",
            "allowed_tools": ["search"],
            "allowed_models": ["gpt-4"],
        }
    )
    d = evaluate("G11", ctx)
    assert d.disposition is Disposition.ALLOW


def test_g11_block_unknown_tool() -> None:
    ctx = GateContext(
        tool_call={
            "tool_id": "shell_exec",
            "allowed_tools": ["search"],
        }
    )
    d = evaluate("G11", ctx)
    assert d.disposition is Disposition.DENY


def test_g11_block_silent_fallback() -> None:
    ctx = GateContext(tool_call={"silent_fallback_attempted": True})
    d = evaluate("G11", ctx)
    assert d.disposition is Disposition.DENY


def test_g11_block_registry_digest_mismatch() -> None:
    ctx = GateContext(tool_call={"registry_digest_ok": False})
    d = evaluate("G11", ctx)
    assert d.disposition is Disposition.DENY


# ---- G12 Tool Argument ----


def test_g12_allow_valid_args() -> None:
    ctx = GateContext(
        tool_call={
            "args": {"target": "/tmp/foo.txt"},
            "is_mutating": True,
            "target_authority": "user_specified",
            "idempotency_key": "k1",
        }
    )
    d = evaluate("G12", ctx)
    assert d.disposition is Disposition.ALLOW


def test_g12_clarify_mutating_inferred_target() -> None:
    ctx = GateContext(
        tool_call={
            "args": {"target": "/data/x"},
            "is_mutating": True,
            "target_authority": "inferred",
        }
    )
    d = evaluate("G12", ctx)
    assert d.disposition is Disposition.CLARIFY
    assert d.stop_condition_violated


def test_g12_shrink_wildcard_mutation() -> None:
    ctx = GateContext(
        tool_call={
            "args": {"target": "**"},
            "is_mutating": True,
            "target_authority": "user_specified",
        }
    )
    d = evaluate("G12", ctx)
    assert d.disposition is Disposition.SHRINK_SCOPE


def test_g12_retry_missing_idempotency() -> None:
    ctx = GateContext(
        tool_call={
            "args": {"target": "/tmp/x"},
            "is_mutating": True,
            "target_authority": "user_specified",
        }
    )
    d = evaluate("G12", ctx)
    assert d.disposition is Disposition.RETRY
