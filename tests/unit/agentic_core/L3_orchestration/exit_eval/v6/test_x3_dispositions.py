"""Unit tests for agentic_core.L3_orchestration.exit_eval.v6.x3_dispositions.

Wave 3.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — high-fan-in exit_eval
module (``x3_dispositions``, fan_in=15). The X3 disposition packet builders:
per-disposition build_x3* functions, the build_x3_packet dispatcher, the
cert-ref extraction fail-closed law (MissingL5CertificationRef), and the
break-glass H3 invariant guards (BreakGlassValidationError). Covers the
app-specific-eval override that forces DENY over a stray ALLOW/COMMIT.
"""

from __future__ import annotations

import pytest

from agentic_core.L3_orchestration.exit_eval.v6.types import (
    ExitReviewPacket,
    SourceType,
    V6Disposition,
    X3AllowPacket,
    X3CommitRequestPacket,
    X3DenyPacket,
    X3EscalatePacket,
    X3SafeAbstainPacket,
)
from agentic_core.L3_orchestration.exit_eval.v6.x2_matrix import AggregateDecision
from agentic_core.L3_orchestration.exit_eval.v6.x3_dispositions import (
    BreakGlassValidationError,
    MissingL5CertificationRef,
    build_x3_packet,
    build_x3a_deny,
    build_x3b_escalate,
    build_x3c_commit_request,
    build_x3d_allow,
    build_x3e_safe_abstain,
    build_x3f_break_glass_allow,
)

_CERT = "l5:cert:abc123"


def _packet(**overrides: object) -> ExitReviewPacket:
    base: dict = {
        "source_type": SourceType.L2_SEALED_ARTIFACT,
        "l5_certification_refs": (_CERT,),
        "trace_root": "trace-1",
        "run_id": "run-1",
        "request_id": "req-1",
        "replay_key": "replay-1",
    }
    base.update(overrides)
    return ExitReviewPacket(**base)  # type: ignore[arg-type]


def _decision(disposition: V6Disposition, **overrides: object) -> AggregateDecision:
    base: dict = {"disposition": disposition}
    base.update(overrides)
    return AggregateDecision(**base)  # type: ignore[arg-type]


class TestCertRefExtraction:
    def test_missing_cert_ref_raises(self) -> None:
        packet = _packet(l5_certification_refs=())
        with pytest.raises(MissingL5CertificationRef):
            build_x3a_deny(packet, _decision(V6Disposition.DENY))

    def test_first_cert_ref_used(self) -> None:
        packet = _packet(l5_certification_refs=("first", "second"))
        pkt = build_x3a_deny(packet, _decision(V6Disposition.DENY))
        assert pkt.l5_certification_ref == "first"


class TestBuildX3aDeny:
    def test_deny_packet_shape(self) -> None:
        decision = _decision(
            V6Disposition.DENY,
            reason_codes=["SANDBOX_BREACH"],
            failed_gate_ids=["X1C"],
            rationale="hard_fail_condition",
        )
        pkt = build_x3a_deny(_packet(), decision)
        assert isinstance(pkt, X3DenyPacket)
        assert pkt.reason_codes == ["SANDBOX_BREACH"]
        assert pkt.failed_gate_ids == ["X1C"]
        assert pkt.user_safe_message  # DENY carries a user-safe message
        assert pkt.l6_failure_packet["rationale"] == "hard_fail_condition"
        assert pkt.trace_root == "trace-1"


class TestBuildX3bEscalate:
    def test_escalate_generates_review_packet_id(self) -> None:
        pkt = build_x3b_escalate(_packet(), _decision(V6Disposition.ESCALATE, reason_codes=["JUDGE_ABSTAINED"]))
        assert isinstance(pkt, X3EscalatePacket)
        assert pkt.review_packet_id.startswith("hitl-")
        assert pkt.trigger_reasons == ["JUDGE_ABSTAINED"]

    def test_escalate_uses_explicit_review_packet_id(self) -> None:
        pkt = build_x3b_escalate(
            _packet(), _decision(V6Disposition.ESCALATE), review_packet_id="hitl-custom"
        )
        assert pkt.review_packet_id == "hitl-custom"

    def test_escalate_falls_back_to_rationale_when_no_codes(self) -> None:
        pkt = build_x3b_escalate(_packet(), _decision(V6Disposition.ESCALATE, rationale="why"))
        assert pkt.trigger_reasons == ["why"]


class TestBuildX3cCommitRequest:
    def test_commit_request_shape(self) -> None:
        packet = _packet(
            policy_hash="ph", state_diff={"blast_radius": "low", "before_snapshot": {"a": 1}}
        )
        pkt = build_x3c_commit_request(packet, _decision(V6Disposition.COMMIT_REQUEST))
        assert isinstance(pkt, X3CommitRequestPacket)
        assert pkt.commit_request_id.startswith("crq-")
        assert pkt.blast_radius == "low"
        assert pkt.before_snapshot == {"a": 1}


class TestBuildX3dAllow:
    def test_allow_uses_explicit_final_response(self) -> None:
        pkt = build_x3d_allow(_packet(), _decision(V6Disposition.ALLOW), final_response="hello")
        assert isinstance(pkt, X3AllowPacket)
        assert pkt.final_response == "hello"

    def test_allow_falls_back_to_output_text(self) -> None:
        pkt = build_x3d_allow(_packet(output={"text": "from-output"}), _decision(V6Disposition.ALLOW))
        assert pkt.final_response == "from-output"

    def test_allow_schema_status_from_output(self) -> None:
        pkt = build_x3d_allow(_packet(output={"schema_valid": False}), _decision(V6Disposition.ALLOW))
        assert pkt.schema_status == "invalid"


class TestBuildX3eSafeAbstain:
    def test_safe_abstain_reason_from_explicit(self) -> None:
        pkt = build_x3e_safe_abstain(
            _packet(), _decision(V6Disposition.SAFE_ABSTAIN), abstain_reason="need clarity"
        )
        assert isinstance(pkt, X3SafeAbstainPacket)
        assert pkt.abstain_reason == "need clarity"

    def test_safe_abstain_reason_from_decision_codes(self) -> None:
        pkt = build_x3e_safe_abstain(
            _packet(), _decision(V6Disposition.SAFE_ABSTAIN, reason_codes=["EVIDENCE_EMPTY"])
        )
        assert "EVIDENCE_EMPTY" in pkt.abstain_reason


class TestBuildX3Packet:
    @pytest.mark.parametrize(
        "disposition,packet_type",
        [
            (V6Disposition.DENY, X3DenyPacket),
            (V6Disposition.ESCALATE, X3EscalatePacket),
            (V6Disposition.ALLOW, X3AllowPacket),
            (V6Disposition.SAFE_ABSTAIN, X3SafeAbstainPacket),
        ],
    )
    def test_dispatch_to_correct_builder(self, disposition: V6Disposition, packet_type: type) -> None:
        pkt = build_x3_packet(_packet(), _decision(disposition))
        assert isinstance(pkt, packet_type)

    def test_commit_request_dispatch(self) -> None:
        pkt = build_x3_packet(_packet(), _decision(V6Disposition.COMMIT_REQUEST))
        assert isinstance(pkt, X3CommitRequestPacket)

    def test_break_glass_dispatch_raises(self) -> None:
        with pytest.raises(ValueError, match="BREAK_GLASS_ALLOW must be invoked"):
            build_x3_packet(_packet(), _decision(V6Disposition.BREAK_GLASS_ALLOW))

    def test_app_eval_failure_overrides_allow_to_deny(self) -> None:
        ase = {"bound": True, "passed": False, "fail_reasons": ["no_fabrication"]}
        pkt = build_x3_packet(_packet(app_specific_eval=ase), _decision(V6Disposition.ALLOW))
        # Belt-and-braces: a failed bound app eval forces DENY even for ALLOW.
        assert isinstance(pkt, X3DenyPacket)
        assert "APP_DIM_FAIL::no_fabrication" in pkt.reason_codes


class TestBuildX3fBreakGlass:
    def _ok_kwargs(self, **overrides: object) -> dict:
        base = dict(
            operator_id="oncall-1",
            capability_token_ref="cap-ref",
            written_justification="prod incident",
            bypassed_gates=["X1B"],
            audit_id="audit-1",
        )
        base.update(overrides)
        return base

    def _bg_packet(self, **token: object) -> ExitReviewPacket:
        tok = {"break_glass": True, "operator_id": "oncall-1"}
        tok.update(token)
        return _packet(capability_token=tok)

    def test_all_h3_invariants_pass_but_packet_fails_closed_on_cert_ref(self) -> None:
        # All H3 break-glass invariants are satisfied (no BreakGlassValidationError),
        # yet build_x3f_break_glass_allow never passes l5_certification_ref into the
        # X3BreakGlassAllowPacket, so its __post_init__ fail-closed cert-ref guard
        # raises ValueError. This documents the real coupling: the break-glass
        # builder cannot emit a packet without a separately-supplied cert ref.
        with pytest.raises(ValueError, match="l5_certification_ref") as exc:
            build_x3f_break_glass_allow(
                self._bg_packet(), _decision(V6Disposition.BREAK_GLASS_ALLOW), **self._ok_kwargs()
            )
        # The failure is the cert-ref guard, NOT an H3 invariant violation.
        assert not isinstance(exc.value, BreakGlassValidationError)

    @pytest.mark.parametrize("forbidden", ["X1A", "X1C"])
    def test_forbidden_bypass_gate_raises(self, forbidden: str) -> None:
        with pytest.raises(BreakGlassValidationError, match="cannot bypass"):
            build_x3f_break_glass_allow(
                self._bg_packet(),
                _decision(V6Disposition.BREAK_GLASS_ALLOW),
                **self._ok_kwargs(bypassed_gates=[forbidden]),
            )

    def test_missing_break_glass_token_raises(self) -> None:
        with pytest.raises(BreakGlassValidationError, match="break_glass=True required"):
            build_x3f_break_glass_allow(
                self._bg_packet(break_glass=False),
                _decision(V6Disposition.BREAK_GLASS_ALLOW),
                **self._ok_kwargs(),
            )

    def test_operator_id_mismatch_raises(self) -> None:
        with pytest.raises(BreakGlassValidationError, match="operator_id mismatch"):
            build_x3f_break_glass_allow(
                self._bg_packet(operator_id="someone-else"),
                _decision(V6Disposition.BREAK_GLASS_ALLOW),
                **self._ok_kwargs(),
            )

    def test_empty_justification_raises(self) -> None:
        with pytest.raises(BreakGlassValidationError, match="written_justification required"):
            build_x3f_break_glass_allow(
                self._bg_packet(),
                _decision(V6Disposition.BREAK_GLASS_ALLOW),
                **self._ok_kwargs(written_justification="   "),
            )

    def test_duration_exceeds_cap_raises(self) -> None:
        with pytest.raises(BreakGlassValidationError, match="duration exceeds"):
            build_x3f_break_glass_allow(
                self._bg_packet(),
                _decision(V6Disposition.BREAK_GLASS_ALLOW),
                **self._ok_kwargs(granted_at_ms=0, expiry_ms=60 * 60 * 1000 + 1),
            )

    def test_empty_audit_id_raises(self) -> None:
        with pytest.raises(BreakGlassValidationError, match="audit_id required"):
            build_x3f_break_glass_allow(
                self._bg_packet(),
                _decision(V6Disposition.BREAK_GLASS_ALLOW),
                **self._ok_kwargs(audit_id=""),
            )

    def test_uwg_bypass_attempt_raises(self) -> None:
        with pytest.raises(BreakGlassValidationError, match="UWG"):
            build_x3f_break_glass_allow(
                self._bg_packet(),
                _decision(V6Disposition.BREAK_GLASS_ALLOW),
                **self._ok_kwargs(bypassed_gates=["U1"]),
            )
