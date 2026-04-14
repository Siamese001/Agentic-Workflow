import pytest
from unittest.mock import MagicMock

_exit_control_hitl = pytest.importorskip(
    "agentic_core.L5_safety.enforcement.exit_control_hitl",
    reason="Requires ExitControlHITL implementation from the monorepo checkout.",
)
AuthorityState = _exit_control_hitl.AuthorityState
BoundedPacket = _exit_control_hitl.BoundedPacket
ExitControlHITL = _exit_control_hitl.ExitControlHITL
HumanDecision = _exit_control_hitl.HumanDecision
HumanReviewInput = _exit_control_hitl.HumanReviewInput
ReClearOutcome = _exit_control_hitl.ReClearOutcome
ReClearResult = _exit_control_hitl.ReClearResult
WriteAuthority = _exit_control_hitl.WriteAuthority


def _mock_gate_result(trace_id: str = "trace-001", reason: str = "low confidence") -> MagicMock:
    gr = MagicMock()
    gr.to_dict.return_value = {
        "trace_id": trace_id,
        "disposition": "ESCALATE_TO_HITL",
        "reason": reason,
        "policy_hash": "sha256:test",
    }
    return gr


def _sealed_artifact(**overrides) -> dict:
    base = {
        "rules_compliant": True,
        "answer_fit": True,
        "safety_clear": True,
        "grounded_replayable": True,
        "confidence_score": 0.65,
        "has_commit_payload": False,
        "raw_content": "SHOULD_BE_EXCLUDED",
    }
    base.update(overrides)
    return base


def _hitl(policy_validator=None) -> ExitControlHITL:
    return ExitControlHITL(policy_validator=policy_validator)


def _approve_input(packet_id: str, reviewer: str = "sme-001") -> HumanReviewInput:
    return HumanReviewInput(
        packet_id=packet_id,
        decision=HumanDecision.APPROVE,
        reviewer_id=reviewer,
        justification="Reviewed and approved after analysis.",
    )


class TestH1H2FreezeAndMaterialize:
    def test_returns_bounded_packet(self):
        hitl = _hitl()
        packet = hitl.freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        assert isinstance(packet, BoundedPacket)

    def test_authority_state_is_frozen(self):
        packet = _hitl().freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        assert packet.authority_state == AuthorityState.FROZEN

    def test_write_authority_is_none(self):
        packet = _hitl().freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        assert packet.write_authority == WriteAuthority.NONE

    def test_packet_has_trace_id(self):
        packet = _hitl().freeze_and_materialize(_mock_gate_result(trace_id="tr-abc"), _sealed_artifact())
        assert packet.trace_id == "tr-abc"

    def test_packet_has_escalation_reason(self):
        packet = _hitl().freeze_and_materialize(
            _mock_gate_result(reason="policy ambiguity"), _sealed_artifact()
        )
        assert "policy ambiguity" in packet.escalation_reason

    def test_packet_has_unique_packet_id(self):
        hitl = _hitl()
        p1 = hitl.freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        p2 = hitl.freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        assert p1.packet_id != p2.packet_id

    def test_raw_content_excluded_from_artifact_summary(self):
        packet = _hitl().freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        assert "raw_content" not in packet.sealed_artifact_summary

    def test_other_artifact_fields_present_in_summary(self):
        packet = _hitl().freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        assert "rules_compliant" in packet.sealed_artifact_summary
        assert "confidence_score" in packet.sealed_artifact_summary

    def test_does_not_mutate_sealed_artifact(self):
        artifact = _sealed_artifact()
        original = dict(artifact)
        _hitl().freeze_and_materialize(_mock_gate_result(), artifact)
        assert artifact == original


class TestBoundedPacketContract:
    def test_to_dict_contains_packet_id(self):
        packet = _hitl().freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        d = packet.to_dict()
        assert "packet_id" in d and d["packet_id"]

    def test_to_dict_contains_trace_id(self):
        packet = _hitl().freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        d = packet.to_dict()
        assert "trace_id" in d

    def test_to_dict_authority_state_is_frozen_string(self):
        packet = _hitl().freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        d = packet.to_dict()
        assert d["authority_state"] == "FROZEN"

    def test_to_dict_write_authority_is_none_string(self):
        packet = _hitl().freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        d = packet.to_dict()
        assert d["write_authority"] == "NONE"

    def test_to_dict_contains_materialized_at_trace(self):
        packet = _hitl().freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        d = packet.to_dict()
        assert "materialized_at_trace" in d and d["materialized_at_trace"]


class TestH4H5ValidateAndReclear:
    def test_approve_with_justification_returns_cleared_allow(self):
        hitl = _hitl()
        packet = hitl.freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        result = hitl.validate_and_reclear(_approve_input(packet.packet_id), packet)
        assert result.outcome == ReClearOutcome.CLEARED_ALLOW

    def test_approve_with_commit_payload_returns_cleared_commit(self):
        hitl = _hitl()
        packet = hitl.freeze_and_materialize(_mock_gate_result(), _sealed_artifact(has_commit_payload=True))
        result = hitl.validate_and_reclear(_approve_input(packet.packet_id), packet)
        assert result.outcome == ReClearOutcome.CLEARED_COMMIT

    def test_cleared_result_has_re_cleared_artifact(self):
        hitl = _hitl()
        packet = hitl.freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        result = hitl.validate_and_reclear(_approve_input(packet.packet_id), packet)
        assert result.re_cleared_artifact is not None

    def test_cleared_result_has_reviewer_id(self):
        hitl = _hitl()
        packet = hitl.freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        result = hitl.validate_and_reclear(_approve_input(packet.packet_id, reviewer="sme-xyz"), packet)
        assert result.reviewer_id == "sme-xyz"

    def test_successful_reclear_removes_packet_from_active(self):
        hitl = _hitl()
        packet = hitl.freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        hitl.validate_and_reclear(_approve_input(packet.packet_id), packet)
        assert packet.packet_id not in hitl._active_packets


class TestBlockedPaths:
    def test_human_deny_returns_blocked(self):
        hitl = _hitl()
        packet = hitl.freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        human_input = HumanReviewInput(
            packet_id=packet.packet_id,
            decision=HumanDecision.DENY,
            reviewer_id="sme-001",
            justification="Output is incorrect.",
        )
        result = hitl.validate_and_reclear(human_input, packet)
        assert result.outcome == ReClearOutcome.BLOCKED

    def test_modify_diff_returns_blocked(self):
        hitl = _hitl()
        packet = hitl.freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        human_input = HumanReviewInput(
            packet_id=packet.packet_id,
            decision=HumanDecision.MODIFY_DIFF,
            reviewer_id="sme-001",
            justification="Applying a fix.",
            proposed_diff={"field": "new_value"},
        )
        result = hitl.validate_and_reclear(human_input, packet)
        assert result.outcome == ReClearOutcome.BLOCKED

    def test_modify_diff_blocked_reason_mentions_bypass(self):
        hitl = _hitl()
        packet = hitl.freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        human_input = HumanReviewInput(
            packet_id=packet.packet_id,
            decision=HumanDecision.MODIFY_DIFF,
            reviewer_id="sme-001",
            justification="patch",
        )
        result = hitl.validate_and_reclear(human_input, packet)
        assert "bypass" in result.reason.lower() or "L5" in result.reason

    def test_packet_id_mismatch_returns_blocked(self):
        hitl = _hitl()
        packet = hitl.freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        human_input = HumanReviewInput(
            packet_id="wrong-packet-id",
            decision=HumanDecision.APPROVE,
            reviewer_id="sme-001",
            justification="Approved.",
        )
        result = hitl.validate_and_reclear(human_input, packet)
        assert result.outcome == ReClearOutcome.BLOCKED

    def test_packet_id_mismatch_blocked_reason_mentions_mismatch(self):
        hitl = _hitl()
        packet = hitl.freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        human_input = HumanReviewInput(
            packet_id="bad-id",
            decision=HumanDecision.APPROVE,
            reviewer_id="sme-001",
            justification="Approved.",
        )
        result = hitl.validate_and_reclear(human_input, packet)
        assert "mismatch" in result.reason.lower()

    def test_missing_reviewer_id_returns_blocked(self):
        hitl = _hitl()
        packet = hitl.freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        human_input = HumanReviewInput(
            packet_id=packet.packet_id,
            decision=HumanDecision.APPROVE,
            reviewer_id="",
            justification="Approved.",
        )
        result = hitl.validate_and_reclear(human_input, packet)
        assert result.outcome == ReClearOutcome.BLOCKED

    def test_missing_justification_returns_blocked(self):
        hitl = _hitl()
        packet = hitl.freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        human_input = HumanReviewInput(
            packet_id=packet.packet_id,
            decision=HumanDecision.APPROVE,
            reviewer_id="sme-001",
            justification="",
        )
        result = hitl.validate_and_reclear(human_input, packet)
        assert result.outcome == ReClearOutcome.BLOCKED

    def test_whitespace_justification_returns_blocked(self):
        hitl = _hitl()
        packet = hitl.freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        human_input = HumanReviewInput(
            packet_id=packet.packet_id,
            decision=HumanDecision.APPROVE,
            reviewer_id="sme-001",
            justification="   ",
        )
        result = hitl.validate_and_reclear(human_input, packet)
        assert result.outcome == ReClearOutcome.BLOCKED

    def test_unfrozen_packet_authority_state_returns_blocked(self):
        hitl = _hitl()
        packet = hitl.freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        tampered = BoundedPacket(
            packet_id=packet.packet_id,
            trace_id=packet.trace_id,
            escalation_reason=packet.escalation_reason,
            sealed_artifact_summary=packet.sealed_artifact_summary,
            authority_state=AuthorityState.ACTIVE,
            write_authority=WriteAuthority.NORMAL,
            materialized_at_trace=packet.materialized_at_trace,
        )
        result = hitl.validate_and_reclear(_approve_input(packet.packet_id), tampered)
        assert result.outcome == ReClearOutcome.BLOCKED


class TestActivePacketStateCleanup:
    def test_deny_removes_packet_from_active_packets(self):
        hitl = _hitl()
        packet = hitl.freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        assert packet.packet_id in hitl._active_packets
        human_input = HumanReviewInput(
            packet_id=packet.packet_id,
            decision=HumanDecision.DENY,
            reviewer_id="sme-001",
            justification="Rejected.",
        )
        hitl.validate_and_reclear(human_input, packet)
        assert packet.packet_id not in hitl._active_packets

    def test_modify_diff_removes_packet_from_active_packets(self):
        hitl = _hitl()
        packet = hitl.freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        assert packet.packet_id in hitl._active_packets
        human_input = HumanReviewInput(
            packet_id=packet.packet_id,
            decision=HumanDecision.MODIFY_DIFF,
            reviewer_id="sme-001",
            justification="Applying diff.",
        )
        hitl.validate_and_reclear(human_input, packet)
        assert packet.packet_id not in hitl._active_packets


class TestCustomPolicyValidator:
    def test_custom_validator_returning_false_blocks_clearance(self):
        hitl = _hitl(policy_validator=lambda artifact, reviewer: False)
        packet = hitl.freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        result = hitl.validate_and_reclear(_approve_input(packet.packet_id), packet)
        assert result.outcome == ReClearOutcome.BLOCKED

    def test_custom_validator_returning_true_clears(self):
        hitl = _hitl(policy_validator=lambda artifact, reviewer: True)
        packet = hitl.freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        result = hitl.validate_and_reclear(_approve_input(packet.packet_id), packet)
        assert result.outcome == ReClearOutcome.CLEARED_ALLOW

    def test_custom_validator_receives_artifact_summary(self):
        received = {}

        def validator(artifact, reviewer):
            received.update(artifact)
            return True

        hitl = _hitl(policy_validator=validator)
        packet = hitl.freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        hitl.validate_and_reclear(_approve_input(packet.packet_id), packet)
        assert "rules_compliant" in received

    def test_custom_validator_receives_reviewer_id(self):
        received = {}

        def validator(artifact, reviewer):
            received["reviewer"] = reviewer
            return True

        hitl = _hitl(policy_validator=validator)
        packet = hitl.freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        hitl.validate_and_reclear(_approve_input(packet.packet_id, reviewer="sme-validator"), packet)
        assert received["reviewer"] == "sme-validator"


class TestReClearResultContract:
    def test_to_dict_contains_outcome(self):
        hitl = _hitl()
        packet = hitl.freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        result = hitl.validate_and_reclear(_approve_input(packet.packet_id), packet)
        d = result.to_dict()
        assert d["outcome"] == "CLEARED_ALLOW"

    def test_to_dict_contains_packet_id(self):
        hitl = _hitl()
        packet = hitl.freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        result = hitl.validate_and_reclear(_approve_input(packet.packet_id), packet)
        d = result.to_dict()
        assert d["packet_id"] == packet.packet_id

    def test_to_dict_contains_trace_id(self):
        hitl = _hitl()
        packet = hitl.freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        result = hitl.validate_and_reclear(_approve_input(packet.packet_id), packet)
        d = result.to_dict()
        assert "trace_id" in d

    def test_blocked_result_re_cleared_artifact_is_none(self):
        hitl = _hitl()
        packet = hitl.freeze_and_materialize(_mock_gate_result(), _sealed_artifact())
        human_input = HumanReviewInput(
            packet_id=packet.packet_id,
            decision=HumanDecision.DENY,
            reviewer_id="sme-001",
            justification="Denied.",
        )
        result = hitl.validate_and_reclear(human_input, packet)
        assert result.re_cleared_artifact is None
