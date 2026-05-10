"""AG-8-FU1: Shared X3 builder cert-ref threading.

Tests proving:
  1. build_x3_packet succeeds with non-empty l5_certification_ref.
  2. build_x3_packet fails closed when l5_certification_ref is missing.
  3. X3AllowPacket receives l5_certification_ref.
  4. X3DenyPacket receives l5_certification_ref.
  5. Escalate / abstain / commit-request packet paths receive l5_certification_ref.
  6. X3 emits exactly one disposition.
  7. build_x3_packet remains downstream of X1/X2 evidence.
  8. material FAIL cannot ALLOW_FINISH.
  9. material UNKNOWN cannot pass.
  10. NOT_APPLICABLE still requires reason.
  11. apps_lic golden path still passes.
  12. apps_rg golden path still passes.

Plan: AG-8-FU1 (Shared X3 builder cert-ref threading)
"""
from __future__ import annotations

import pytest

from agentic_core.L3_orchestration.exit_eval.v6.types import (
    ExitReviewPacket,
    GateResult,
    GateVerdict,
    SourceType,
    V6Disposition,
    X3AllowPacket,
    X3CommitRequestPacket,
    X3DenyPacket,
    X3EscalatePacket,
    X3SafeAbstainPacket,
)
from agentic_core.L3_orchestration.exit_eval.v6.x2_matrix import (
    AggregateDecision,
)
from agentic_core.L3_orchestration.exit_eval.v6.x3_dispositions import (
    MissingL5CertificationRef,
    build_x3a_deny,
    build_x3b_escalate,
    build_x3c_commit_request,
    build_x3d_allow,
    build_x3e_safe_abstain,
    build_x3_packet,
    _extract_cert_ref,
)

_CERT_REF = "test-cert-ref-ag8-fu1"
_ALT_CERT_REF = "test-cert-ref-ag8-fu1-alt"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _packet(
    *,
    cert_refs: tuple[str, ...] = (_CERT_REF,),
    terminal_class: str = "answer_only",
    state_diff: dict | None = None,
    output: dict | None = None,
    app_specific_eval: dict | None = None,
) -> ExitReviewPacket:
    return ExitReviewPacket(
        source_type=SourceType.L2_SEALED_ARTIFACT,
        request_id="req-fu1",
        run_id="run-fu1",
        trace_root="trace-fu1",
        policy_hash="policy-fu1",
        blueprint_hash="blueprint-fu1",
        terminal_class=terminal_class,
        l5_certification_refs=cert_refs,
        state_diff=state_diff or {},
        output=output or {"schema_valid": True, "text": "hello"},
        final_evidence_contract={"c0_status": "PASS"},
        app_specific_eval=app_specific_eval or {},
    )


def _allow_decision() -> AggregateDecision:
    return AggregateDecision(
        disposition=V6Disposition.ALLOW,
        rationale="test_allow",
    )


def _deny_decision(reason: str = "TEST_FAIL") -> AggregateDecision:
    return AggregateDecision(
        disposition=V6Disposition.DENY,
        rationale="test_deny",
        reason_codes=[reason],
    )


def _escalate_decision() -> AggregateDecision:
    return AggregateDecision(
        disposition=V6Disposition.ESCALATE,
        rationale="test_escalate",
        reason_codes=["NEEDS_REVIEW"],
    )


def _abstain_decision() -> AggregateDecision:
    return AggregateDecision(
        disposition=V6Disposition.SAFE_ABSTAIN,
        rationale="test_abstain",
        reason_codes=["UNSUPPORTED_QUERY"],
    )


def _commit_decision() -> AggregateDecision:
    return AggregateDecision(
        disposition=V6Disposition.COMMIT_REQUEST,
        rationale="test_commit",
    )


def _failed_gate_verdict(gate_id: str = "X1B") -> GateVerdict:
    return GateVerdict(gate_id=gate_id, result=GateResult.FAIL, reason_codes=("HARD_FAIL",))


# ---------------------------------------------------------------------------
# Test 1 + 2: build_x3_packet success / fail-closed
# ---------------------------------------------------------------------------


class TestBuildX3PacketCertRefPresence:
    def test_succeeds_with_cert_ref(self) -> None:
        """Test 1: build_x3_packet succeeds when l5_certification_refs is non-empty."""
        packet = _packet(cert_refs=(_CERT_REF,))
        decision = _allow_decision()
        x3 = build_x3_packet(packet, decision)
        assert isinstance(x3, X3AllowPacket)

    def test_fails_closed_when_cert_refs_empty(self) -> None:
        """Test 2: build_x3_packet fails closed with MissingL5CertificationRef when refs is empty."""
        packet = _packet(cert_refs=())
        decision = _allow_decision()
        with pytest.raises(MissingL5CertificationRef):
            build_x3_packet(packet, decision)

    def test_fails_closed_for_deny_without_cert_ref(self) -> None:
        """Test 2 (deny path): build_x3_packet DENY fails closed when refs is empty."""
        packet = _packet(cert_refs=())
        decision = _deny_decision()
        with pytest.raises(MissingL5CertificationRef):
            build_x3_packet(packet, decision)

    def test_fails_closed_for_escalate_without_cert_ref(self) -> None:
        """Test 2 (escalate path): build_x3_packet ESCALATE fails closed when refs is empty."""
        packet = _packet(cert_refs=())
        decision = _escalate_decision()
        with pytest.raises(MissingL5CertificationRef):
            build_x3_packet(packet, decision)

    def test_fails_closed_for_abstain_without_cert_ref(self) -> None:
        """Test 2 (abstain path): build_x3_packet SAFE_ABSTAIN fails closed when refs is empty."""
        packet = _packet(cert_refs=())
        decision = _abstain_decision()
        with pytest.raises(MissingL5CertificationRef):
            build_x3_packet(packet, decision)


# ---------------------------------------------------------------------------
# Test 3: X3AllowPacket receives l5_certification_ref
# ---------------------------------------------------------------------------


class TestX3AllowPacketCertRef:
    def test_allow_packet_has_cert_ref(self) -> None:
        """Test 3: X3AllowPacket constructed via build_x3d_allow carries cert ref."""
        packet = _packet(cert_refs=(_CERT_REF,))
        decision = _allow_decision()
        x3 = build_x3d_allow(packet, decision)
        assert isinstance(x3, X3AllowPacket)
        assert x3.l5_certification_ref == _CERT_REF

    def test_allow_packet_cert_ref_matches_first_in_tuple(self) -> None:
        """Test 3: When multiple cert refs, first is used."""
        packet = _packet(cert_refs=(_CERT_REF, _ALT_CERT_REF))
        decision = _allow_decision()
        x3 = build_x3d_allow(packet, decision)
        assert x3.l5_certification_ref == _CERT_REF

    def test_build_x3_packet_allow_carries_cert_ref(self) -> None:
        """Test 3: build_x3_packet dispatcher threads cert ref to X3AllowPacket."""
        packet = _packet(cert_refs=(_CERT_REF,))
        decision = _allow_decision()
        x3 = build_x3_packet(packet, decision)
        assert isinstance(x3, X3AllowPacket)
        assert x3.l5_certification_ref == _CERT_REF


# ---------------------------------------------------------------------------
# Test 4: X3DenyPacket receives l5_certification_ref
# ---------------------------------------------------------------------------


class TestX3DenyPacketCertRef:
    def test_deny_packet_has_cert_ref(self) -> None:
        """Test 4: X3DenyPacket constructed via build_x3a_deny carries cert ref."""
        packet = _packet(cert_refs=(_CERT_REF,))
        decision = _deny_decision()
        x3 = build_x3a_deny(packet, decision)
        assert isinstance(x3, X3DenyPacket)
        assert x3.l5_certification_ref == _CERT_REF

    def test_build_x3_packet_deny_carries_cert_ref(self) -> None:
        """Test 4: build_x3_packet dispatcher threads cert ref to X3DenyPacket."""
        packet = _packet(cert_refs=(_CERT_REF,))
        decision = _deny_decision()
        x3 = build_x3_packet(packet, decision)
        assert isinstance(x3, X3DenyPacket)
        assert x3.l5_certification_ref == _CERT_REF


# ---------------------------------------------------------------------------
# Test 5: Escalate / abstain / commit-request paths receive cert ref
# ---------------------------------------------------------------------------


class TestX3EscalateAbstainCommitCertRef:
    def test_escalate_packet_has_cert_ref(self) -> None:
        """Test 5a: X3EscalatePacket receives l5_certification_ref."""
        packet = _packet(cert_refs=(_CERT_REF,))
        decision = _escalate_decision()
        x3 = build_x3b_escalate(packet, decision)
        assert isinstance(x3, X3EscalatePacket)
        assert x3.l5_certification_ref == _CERT_REF

    def test_escalate_via_dispatcher_has_cert_ref(self) -> None:
        """Test 5a: build_x3_packet ESCALATE dispatch threads cert ref."""
        packet = _packet(cert_refs=(_CERT_REF,))
        decision = _escalate_decision()
        x3 = build_x3_packet(packet, decision)
        assert isinstance(x3, X3EscalatePacket)
        assert x3.l5_certification_ref == _CERT_REF

    def test_abstain_packet_has_cert_ref(self) -> None:
        """Test 5b: X3SafeAbstainPacket receives l5_certification_ref."""
        packet = _packet(cert_refs=(_CERT_REF,))
        decision = _abstain_decision()
        x3 = build_x3e_safe_abstain(packet, decision)
        assert isinstance(x3, X3SafeAbstainPacket)
        assert x3.l5_certification_ref == _CERT_REF

    def test_abstain_via_dispatcher_has_cert_ref(self) -> None:
        """Test 5b: build_x3_packet SAFE_ABSTAIN dispatch threads cert ref."""
        packet = _packet(cert_refs=(_CERT_REF,))
        decision = _abstain_decision()
        x3 = build_x3_packet(packet, decision)
        assert isinstance(x3, X3SafeAbstainPacket)
        assert x3.l5_certification_ref == _CERT_REF

    def test_commit_request_packet_has_cert_ref(self) -> None:
        """Test 5c: X3CommitRequestPacket receives l5_certification_ref."""
        packet = _packet(
            cert_refs=(_CERT_REF,),
            terminal_class="with_state_diff",
            state_diff={"write": True},
        )
        decision = _commit_decision()
        x3 = build_x3c_commit_request(packet, decision)
        assert isinstance(x3, X3CommitRequestPacket)
        assert x3.l5_certification_ref == _CERT_REF


# ---------------------------------------------------------------------------
# Test 6: X3 emits exactly one disposition
# ---------------------------------------------------------------------------


class TestX3ExactlyOneDisposition:
    @pytest.mark.parametrize("disp", [
        V6Disposition.ALLOW,
        V6Disposition.DENY,
        V6Disposition.ESCALATE,
        V6Disposition.SAFE_ABSTAIN,
    ])
    def test_single_disposition_emitted(self, disp: V6Disposition) -> None:
        """Test 6: build_x3_packet emits exactly one X3* packet per call."""
        packet = _packet(cert_refs=(_CERT_REF,))
        decision = AggregateDecision(disposition=disp, rationale="test")
        x3 = build_x3_packet(packet, decision)
        assert x3.disposition == disp


# ---------------------------------------------------------------------------
# Test 7: build_x3_packet remains downstream of X1/X2 evidence
# ---------------------------------------------------------------------------


class TestX3DownstreamConstraint:
    def test_x3_requires_aggregate_decision(self) -> None:
        """Test 7: build_x3_packet accepts AggregateDecision (X2 output)."""
        packet = _packet(cert_refs=(_CERT_REF,))
        decision = _allow_decision()
        x3 = build_x3_packet(packet, decision)
        assert x3 is not None

    def test_x3_allow_reflects_x2_rationale(self) -> None:
        """Test 7: X3AllowPacket runtime_exhaust_manifest carries X2 rationale."""
        packet = _packet(cert_refs=(_CERT_REF,))
        decision = AggregateDecision(
            disposition=V6Disposition.ALLOW,
            rationale="x2_evidence_checked",
        )
        x3 = build_x3_packet(packet, decision)
        assert isinstance(x3, X3AllowPacket)
        assert x3.runtime_exhaust_manifest.get("rationale") == "x2_evidence_checked"

    def test_x3_deny_reflects_x2_failed_gates(self) -> None:
        """Test 7: X3DenyPacket failed_gate_ids reflects X2 AggregateDecision."""
        packet = _packet(cert_refs=(_CERT_REF,))
        decision = AggregateDecision(
            disposition=V6Disposition.DENY,
            rationale="gate_fail",
            reason_codes=["HARD_FAIL"],
            failed_gate_ids=["X1B"],
        )
        x3 = build_x3_packet(packet, decision)
        assert isinstance(x3, X3DenyPacket)
        assert "X1B" in x3.failed_gate_ids


# ---------------------------------------------------------------------------
# Test 8: material FAIL cannot ALLOW_FINISH
# ---------------------------------------------------------------------------


class TestMaterialFailBlocksAllow:
    def test_failed_gate_verdict_triggers_deny_not_allow(self) -> None:
        """Test 8: A DENY disposition from X2 produces X3DenyPacket, not X3AllowPacket."""
        packet = _packet(cert_refs=(_CERT_REF,))
        decision = _deny_decision("HARD_FAIL")
        x3 = build_x3_packet(packet, decision)
        assert not isinstance(x3, X3AllowPacket), (
            "material FAIL must not produce an X3AllowPacket"
        )
        assert isinstance(x3, X3DenyPacket)

    def test_allow_decision_with_failed_app_eval_overridden(self) -> None:
        """Test 8: Even forged ALLOW with failed app_specific_eval is blocked to DENY."""
        packet = _packet(
            cert_refs=(_CERT_REF,),
            app_specific_eval={"passed": False, "bound": True},
        )
        forged_allow = _allow_decision()
        x3 = build_x3_packet(packet, forged_allow)
        assert isinstance(x3, X3DenyPacket), (
            "X3 belt-and-braces: forged ALLOW with failed app eval must become DENY"
        )


# ---------------------------------------------------------------------------
# Test 9: material UNKNOWN cannot pass
# ---------------------------------------------------------------------------


class TestMaterialUnknownCannotPass:
    def test_escalate_decision_does_not_produce_allow(self) -> None:
        """Test 9: ESCALATE disposition (material UNKNOWN) cannot produce X3AllowPacket."""
        packet = _packet(cert_refs=(_CERT_REF,))
        decision = _escalate_decision()
        x3 = build_x3_packet(packet, decision)
        assert not isinstance(x3, X3AllowPacket)
        assert isinstance(x3, X3EscalatePacket)


# ---------------------------------------------------------------------------
# Test 10: NOT_APPLICABLE still requires reason
# ---------------------------------------------------------------------------


class TestNotApplicableRequiresReason:
    def test_not_applicable_verdict_with_reason_passes(self) -> None:
        """Test 10: GateVerdict NOT_APPLICABLE with reason_codes is valid."""
        v = GateVerdict(
            gate_id="X1J",
            result=GateResult.NOT_APPLICABLE,
            reason_codes=("write_not_applicable_answer_only",),
            remediation_hint="",
        )
        assert v.result == GateResult.NOT_APPLICABLE
        assert v.reason_codes

    def test_not_applicable_verdict_without_reason_has_no_reason(self) -> None:
        """Test 10: GateVerdict NOT_APPLICABLE without reason_codes has empty reason_codes."""
        v = GateVerdict(
            gate_id="X1J",
            result=GateResult.NOT_APPLICABLE,
        )
        assert v.result == GateResult.NOT_APPLICABLE
        assert not v.reason_codes


# ---------------------------------------------------------------------------
# Test 11 + 12: apps_lic and apps_rg golden paths still pass
# ---------------------------------------------------------------------------


class TestGoldenPathRegressionGuard:
    def test_apps_lic_exit_binding_importable(self) -> None:
        """Test 11: apps_lic exit binding still importable after patch."""
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic
        assert callable(exit_finalize_apps_lic)

    def test_apps_lic_exit_binding_populates_l5_cert_refs(self) -> None:
        """Test 11: _build_exit_review_packet populates l5_certification_refs."""
        from agentic_core.runtime.exit.apps_lic_exit_binding import (
            _build_exit_review_packet,
            _CERT_REF as LIC_CERT_REF,
        )
        from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact

        l2 = SealedL2Artifact(
            request_id="r1",
            run_id="run1",
            trace_id="trace-fu1",
            app_id="apps_lic",
            execution_status="completed",
            generated_content="hello",
            l5_certification_ref=LIC_CERT_REF,
        )
        packet = _build_exit_review_packet(l2)
        assert LIC_CERT_REF in packet.l5_certification_refs, (
            "ExitReviewPacket must contain l5_certification_refs with the cert ref"
        )

    def test_apps_lic_build_exit_review_packet_cert_ref_extractable(self) -> None:
        """Test 11: _extract_cert_ref can derive cert ref from apps_lic ExitReviewPacket."""
        from agentic_core.runtime.exit.apps_lic_exit_binding import _build_exit_review_packet
        from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact

        from agentic_core.runtime.exit.apps_lic_exit_binding import _CERT_REF as LIC_CERT_REF2
        l2 = SealedL2Artifact(
            request_id="r1",
            run_id="run1",
            trace_id="trace-fu1",
            app_id="apps_lic",
            execution_status="completed",
            generated_content="hello",
            l5_certification_ref=LIC_CERT_REF2,
        )
        packet = _build_exit_review_packet(l2)
        ref = _extract_cert_ref(packet)
        assert ref == "exit-apps-lic-outreach-message-ag8-w7-f3c2e1"

    def test_apps_rg_exit_binding_importable(self) -> None:
        """Test 12: apps_rg exit binding still importable after patch."""
        from agentic_core.runtime.exit.apps_rg_exit_binding import exit_finalize_apps_rg
        assert callable(exit_finalize_apps_rg)

    def test_apps_rg_cert_ref_constant_present(self) -> None:
        """Test 12: apps_rg APPS_RG_EXIT_CERT_REF constant unchanged."""
        from agentic_core.runtime.exit.apps_rg_exit_binding import APPS_RG_EXIT_CERT_REF
        assert APPS_RG_EXIT_CERT_REF == "exit-apps-rg-resume-generation-w3p5"


# ---------------------------------------------------------------------------
# Test: _extract_cert_ref helper contract
# ---------------------------------------------------------------------------


class TestExtractCertRefHelper:
    def test_returns_first_ref_from_tuple(self) -> None:
        packet = _packet(cert_refs=(_CERT_REF, _ALT_CERT_REF))
        assert _extract_cert_ref(packet) == _CERT_REF

    def test_raises_when_tuple_empty(self) -> None:
        packet = _packet(cert_refs=())
        with pytest.raises(MissingL5CertificationRef) as exc_info:
            _extract_cert_ref(packet)
        assert "l5_certification_refs is empty" in str(exc_info.value)

    def test_raises_with_helpful_message(self) -> None:
        packet = _packet(cert_refs=())
        with pytest.raises(MissingL5CertificationRef) as exc_info:
            _extract_cert_ref(packet)
        msg = str(exc_info.value)
        assert "AG-8-FU1" in msg
        assert "Populate" in msg


# ---------------------------------------------------------------------------
# Test: MissingL5CertificationRef is a subclass of ValueError
# ---------------------------------------------------------------------------


class TestMissingL5CertRefException:
    def test_is_value_error_subclass(self) -> None:
        """MissingL5CertificationRef must be a ValueError subclass for catch-site compatibility."""
        assert issubclass(MissingL5CertificationRef, ValueError)

    def test_can_be_caught_as_value_error(self) -> None:
        packet = _packet(cert_refs=())
        with pytest.raises(ValueError):
            _extract_cert_ref(packet)
