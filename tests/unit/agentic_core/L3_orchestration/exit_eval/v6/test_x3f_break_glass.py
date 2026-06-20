"""Tests for v6 X3F BREAK_GLASS_ALLOW disposition (v4_hardening §H3).

Wave 1 of exit-eval-v6 deferred-scope completion. Resolves the H3 X3E
naming divergence by adding X3F as a distinct disposition for operator
emergency override, preserving canonical X3E=SAFE_ABSTAIN_CLARIFY.
"""

from __future__ import annotations

import time

import pytest

from agentic_core.L3_orchestration.exit_eval.v6 import (
    AggregateDecision,
    BreakGlassValidationError,
    V6Disposition,
    X3BreakGlassAllowPacket,
    build_x3_packet,
    build_x3f_break_glass_allow,
)
from agentic_core.L3_orchestration.exit_eval.v6.x3_dispositions import (
    _X3F_FORBIDDEN_BYPASS_GATES,
    _X3F_MAX_DURATION_MS,
    _X3F_POST_MORTEM_OFFSET_MS,
)

from tests.unit.agentic_core.L3_orchestration.exit_eval.v6._fixtures import base_packet


def _ok_kwargs(**overrides):
    """Default valid X3F kwargs; tests override one field at a time."""
    defaults = dict(
        operator_id="oncall-alice",
        capability_token_ref="token-abc123",
        written_justification="Production incident #4711 - payment-flow stuck",
        bypassed_gates=["X1B", "X1D", "X1E"],
        audit_id="audit-row-9000",
        pages_emitted=["pagerduty:incident:4711"],
        customer_facing_l4_commit_allowed=False,
    )
    defaults.update(overrides)
    return defaults


def _packet_with_break_glass_token(**token_overrides):
    """Packet with a valid break-glass capability token."""
    p = base_packet()
    p.capability_token = {
        "break_glass": True,
        "operator_id": "oncall-alice",
        "expired": False,
        **token_overrides,
    }
    return p


def _decision() -> AggregateDecision:
    """Stand-in decision; not used by X3F (which is operator-invoked)."""
    return AggregateDecision(
        disposition=V6Disposition.BREAK_GLASS_ALLOW,
        rationale="operator break-glass invocation",
        reason_codes=[],
        triggering_verdicts=[],
        failed_gate_ids=[],
    )


# ---------- Happy path ----------


def test_x3f_v6_disposition_enum_present() -> None:
    """Wave 1 acceptance: V6Disposition.BREAK_GLASS_ALLOW exists with value X3F."""
    assert V6Disposition.BREAK_GLASS_ALLOW.value == "X3F"
    assert V6Disposition.BREAK_GLASS_ALLOW is not V6Disposition.SAFE_ABSTAIN
    # X3E preserved as SAFE_ABSTAIN per canonical 05.5
    assert V6Disposition.SAFE_ABSTAIN.value == "X3E"


def test_x3f_minimal_valid_invocation_returns_packet() -> None:
    p = _packet_with_break_glass_token()
    pkt = build_x3f_break_glass_allow(p, _decision(), **_ok_kwargs())
    assert isinstance(pkt, X3BreakGlassAllowPacket)
    assert pkt.disposition is V6Disposition.BREAK_GLASS_ALLOW
    assert pkt.operator_id == "oncall-alice"
    assert pkt.audit_id == "audit-row-9000"
    assert pkt.bypassed_gates == ["X1B", "X1D", "X1E"]
    assert pkt.customer_facing_l4_commit_allowed is False
    assert pkt.expiry_ms - pkt.granted_at_ms == _X3F_MAX_DURATION_MS
    assert pkt.post_mortem_due_at_ms == pkt.granted_at_ms + _X3F_POST_MORTEM_OFFSET_MS
    assert pkt.trace_root == p.trace_root


# ---------- H3.1: forbidden gate bypass ----------


@pytest.mark.parametrize("forbidden_gate", sorted(_X3F_FORBIDDEN_BYPASS_GATES))
def test_x3f_rejects_x1a_x1c_bypass(forbidden_gate: str) -> None:
    """H3.1: break-glass cannot bypass X1A (policy) or X1C (sandbox/mutation)."""
    p = _packet_with_break_glass_token()
    with pytest.raises(BreakGlassValidationError, match="H3.1"):
        build_x3f_break_glass_allow(
            p, _decision(), **_ok_kwargs(bypassed_gates=[forbidden_gate, "X1D"])
        )


def test_x3f_rejects_uwg_gate_bypass() -> None:
    """H3.1: UWG verification (U1/U2/U3) is never bypassable."""
    p = _packet_with_break_glass_token()
    with pytest.raises(BreakGlassValidationError, match="UWG"):
        build_x3f_break_glass_allow(
            p, _decision(), **_ok_kwargs(bypassed_gates=["X1D", "U1"])
        )


# ---------- H3.2.1: capability token ----------


def test_x3f_rejects_when_token_missing_break_glass_flag() -> None:
    """H3.2.1: capability_token must declare break_glass=True."""
    p = base_packet()
    p.capability_token = {"break_glass": False, "operator_id": "oncall-alice"}
    with pytest.raises(BreakGlassValidationError, match="break_glass=True"):
        build_x3f_break_glass_allow(p, _decision(), **_ok_kwargs())


def test_x3f_rejects_empty_operator_id() -> None:
    p = _packet_with_break_glass_token()
    with pytest.raises(BreakGlassValidationError, match="operator_id required"):
        build_x3f_break_glass_allow(p, _decision(), **_ok_kwargs(operator_id=""))


def test_x3f_rejects_operator_id_mismatch_with_token() -> None:
    """H3.2.1: token's operator_id must match the invoking operator_id."""
    p = _packet_with_break_glass_token(operator_id="oncall-bob")
    with pytest.raises(BreakGlassValidationError, match="operator_id mismatch"):
        build_x3f_break_glass_allow(p, _decision(), **_ok_kwargs(operator_id="oncall-alice"))


def test_x3f_rejects_expired_token() -> None:
    p = _packet_with_break_glass_token(expired=True)
    with pytest.raises(BreakGlassValidationError, match="expired"):
        build_x3f_break_glass_allow(p, _decision(), **_ok_kwargs())


# ---------- H3.2.2: written justification + expiry ----------


@pytest.mark.parametrize("justification", ["", "   ", "\n\t"])
def test_x3f_rejects_blank_justification(justification: str) -> None:
    p = _packet_with_break_glass_token()
    with pytest.raises(BreakGlassValidationError, match="written_justification"):
        build_x3f_break_glass_allow(
            p, _decision(), **_ok_kwargs(written_justification=justification)
        )


def test_x3f_rejects_expiry_beyond_60min_cap() -> None:
    """H3.2.2: hard 60-minute cap on break-glass duration."""
    p = _packet_with_break_glass_token()
    grant = 1_000_000_000_000
    too_long = grant + _X3F_MAX_DURATION_MS + 1
    with pytest.raises(BreakGlassValidationError, match="duration exceeds"):
        build_x3f_break_glass_allow(
            p, _decision(), **_ok_kwargs(granted_at_ms=grant, expiry_ms=too_long)
        )


def test_x3f_rejects_expiry_at_or_before_grant() -> None:
    p = _packet_with_break_glass_token()
    grant = 1_000_000_000_000
    with pytest.raises(BreakGlassValidationError, match="must be after"):
        build_x3f_break_glass_allow(
            p, _decision(), **_ok_kwargs(granted_at_ms=grant, expiry_ms=grant)
        )


def test_x3f_accepts_expiry_exactly_at_60min_boundary() -> None:
    """Boundary: exactly 60 min is allowed; one ms beyond is not."""
    p = _packet_with_break_glass_token()
    grant = 1_000_000_000_000
    expiry = grant + _X3F_MAX_DURATION_MS
    pkt = build_x3f_break_glass_allow(
        p, _decision(), **_ok_kwargs(granted_at_ms=grant, expiry_ms=expiry)
    )
    assert pkt.expiry_ms - pkt.granted_at_ms == _X3F_MAX_DURATION_MS


def test_x3f_default_expiry_is_60min_from_grant() -> None:
    p = _packet_with_break_glass_token()
    pkt = build_x3f_break_glass_allow(p, _decision(), **_ok_kwargs())
    assert pkt.expiry_ms - pkt.granted_at_ms == _X3F_MAX_DURATION_MS


# ---------- H3.2.4: audit row ----------


def test_x3f_rejects_blank_audit_id() -> None:
    p = _packet_with_break_glass_token()
    with pytest.raises(BreakGlassValidationError, match="audit_id"):
        build_x3f_break_glass_allow(p, _decision(), **_ok_kwargs(audit_id=""))


# ---------- H3.3: post-mortem ----------


def test_x3f_post_mortem_set_to_24h_after_grant() -> None:
    p = _packet_with_break_glass_token()
    grant = 1_500_000_000_000
    pkt = build_x3f_break_glass_allow(
        p, _decision(), **_ok_kwargs(granted_at_ms=grant)
    )
    assert pkt.post_mortem_due_at_ms == grant + _X3F_POST_MORTEM_OFFSET_MS
    # 24h
    assert pkt.post_mortem_due_at_ms - grant == 24 * 60 * 60 * 1000


# ---------- H3.2.5: customer-facing L4 commit guard ----------


def test_x3f_default_disallows_customer_facing_l4_commit() -> None:
    p = _packet_with_break_glass_token()
    pkt = build_x3f_break_glass_allow(p, _decision(), **_ok_kwargs())
    assert pkt.customer_facing_l4_commit_allowed is False


def test_x3f_explicit_customer_l4_commit_allowed_recorded() -> None:
    """Operator can flip the flag explicitly; H3.2.5 still requires post-incident
    ratification by a separate operator. This builder records intent only."""
    p = _packet_with_break_glass_token()
    pkt = build_x3f_break_glass_allow(
        p, _decision(), **_ok_kwargs(customer_facing_l4_commit_allowed=True)
    )
    assert pkt.customer_facing_l4_commit_allowed is True


# ---------- Dispatcher behavior ----------


def test_dispatcher_rejects_x3f_via_aggregate_dispatch() -> None:
    """build_x3_packet must NOT auto-dispatch to X3F — H3.2.1 capability gate."""
    p = base_packet()
    decision = AggregateDecision(
        disposition=V6Disposition.BREAK_GLASS_ALLOW,
        rationale="not an operator invocation",
        reason_codes=[],
        triggering_verdicts=[],
        failed_gate_ids=[],
    )
    with pytest.raises(ValueError, match="must be invoked via build_x3f_break_glass_allow"):
        build_x3_packet(p, decision)


def test_dispatcher_still_routes_x3e_safe_abstain() -> None:
    """Regression: X3E SAFE_ABSTAIN must still dispatch normally; X3F doesn't
    affect X3E."""
    p = base_packet()
    decision = AggregateDecision(
        disposition=V6Disposition.SAFE_ABSTAIN,
        rationale="abstain",
        reason_codes=[],
        triggering_verdicts=[],
        failed_gate_ids=[],
    )
    pkt = build_x3_packet(p, decision)
    # Compare by class name not isinstance — other tests in the suite may
    # import X3SafeAbstainPacket via a re-export path that pylance/pytest
    # treats as a distinct class object even though the runtime type is the same.
    assert type(pkt).__name__ == "X3SafeAbstainPacket"
    assert pkt.disposition is V6Disposition.SAFE_ABSTAIN
    assert pkt.disposition.value == "X3E"
    assert pkt.abstain_reason == "abstain"


# ---------- OTEL span catalog ----------


def test_x3f_span_in_catalog() -> None:
    """OTEL: exit.x3f.break_glass_allow_emit must be in canonical catalog."""
    from agentic_core.L3_orchestration.exit_eval.v6 import EXIT_V6_SPAN_CATALOG

    assert "exit.x3f.break_glass_allow_emit" in EXIT_V6_SPAN_CATALOG


# ---------- Distinctness from X3E ----------


def test_x3f_packet_distinct_from_x3e_packet() -> None:
    """Wave 1 acceptance: X3F packet type is distinct from X3E packet type."""
    from agentic_core.L3_orchestration.exit_eval.v6.types import X3SafeAbstainPacket

    p = _packet_with_break_glass_token()
    x3f_pkt = build_x3f_break_glass_allow(p, _decision(), **_ok_kwargs())
    assert not isinstance(x3f_pkt, X3SafeAbstainPacket)
    assert type(x3f_pkt).__name__ == "X3BreakGlassAllowPacket"


def test_x3f_records_grant_time_when_not_supplied() -> None:
    """Default granted_at_ms uses wall clock; verify it's reasonable."""
    p = _packet_with_break_glass_token()
    before = int(time.time() * 1000)
    pkt = build_x3f_break_glass_allow(p, _decision(), **_ok_kwargs())
    after = int(time.time() * 1000)
    assert before <= pkt.granted_at_ms <= after
