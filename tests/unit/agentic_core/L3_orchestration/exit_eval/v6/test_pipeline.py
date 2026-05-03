"""Tests for the v6 end-to-end ExitEvalPipeline."""

from __future__ import annotations

from agentic_core.L3_orchestration.exit_eval.v6 import (
    ExitEvalPipeline,
    UwgOutcome,
    V6Disposition,
    default_backends,
    run_exit_eval,
)
from agentic_core.L3_orchestration.exit_eval.v6.types import (
    X3AllowPacket,
    X3CommitRequestPacket,
    X3DenyPacket,
    X3SafeAbstainPacket,
)

from tests.unit.agentic_core.L3_orchestration.exit_eval.v6._fixtures import base_receipts


def test_pipeline_clean_answer_only_returns_x3d() -> None:
    result = run_exit_eval(base_receipts())
    assert result.disposition is V6Disposition.ALLOW
    assert isinstance(result.x3_packet, X3AllowPacket)
    assert len(result.verdicts) == 10
    assert result.uwg_receipt is None
    assert result.preflight_failures == []


def test_normalize_populates_app_contract_fields_from_receipts() -> None:
    """APPS-DOM runtime binding — receipts top-level app_id/rubric_ref/... land on packet."""
    from agentic_core.L3_orchestration.exit_eval.v6.preflight import normalize_to_packet
    receipts = base_receipts(
        app_id="apps_qna",
        task_class="qna_pack_build",
        rubric_ref="aer::apps_qna::qna_pack_build::v1",
        threshold_profile_ref="atp::apps_qna::qna_pack_build::v1",
        grader_roster_ref="agr::apps_qna::qna_pack_build::v1",
    )
    pkt = normalize_to_packet(receipts)
    assert pkt.app_id == "apps_qna"
    assert pkt.task_class == "qna_pack_build"
    assert pkt.rubric_ref == "aer::apps_qna::qna_pack_build::v1"
    assert pkt.threshold_profile_ref == "atp::apps_qna::qna_pack_build::v1"
    assert pkt.grader_roster_ref == "agr::apps_qna::qna_pack_build::v1"


def test_normalize_populates_app_contract_fields_from_route_contract() -> None:
    """Fallback: fields under route_contract also land on packet when top-level absent."""
    from agentic_core.L3_orchestration.exit_eval.v6.preflight import normalize_to_packet
    receipts = base_receipts(
        route_contract={
            "route_id": "R3",
            "policy_hash": "pol::v1",
            "blueprint_hash": "bp::v1",
            "prompt_hash": "ph::v1",
            "app_id": "apps_lic",
            "rubric_ref": "aer::apps_lic::outreach::v1",
            "threshold_profile_ref": "atp::apps_lic::outreach::v1",
        },
    )
    pkt = normalize_to_packet(receipts)
    assert pkt.app_id == "apps_lic"
    assert pkt.rubric_ref == "aer::apps_lic::outreach::v1"
    assert pkt.threshold_profile_ref == "atp::apps_lic::outreach::v1"


def test_normalize_preserves_empty_defaults_when_fields_absent() -> None:
    """Backward compat — packet app contract fields are "" when receipts don't carry them."""
    from agentic_core.L3_orchestration.exit_eval.v6.preflight import normalize_to_packet
    pkt = normalize_to_packet(base_receipts())
    assert pkt.app_id == ""
    assert pkt.rubric_ref == ""
    assert pkt.threshold_profile_ref == ""


def test_pipeline_preflight_failure_emits_x3a() -> None:
    receipts = base_receipts(policy_hash="")  # §5.0 immediate-fail
    result = run_exit_eval(receipts)
    assert result.disposition is V6Disposition.DENY
    assert isinstance(result.x3_packet, X3DenyPacket)
    assert any(f.reason_code == "POLICY_HASH_MISSING" for f in result.preflight_failures)
    # Pipeline halts before X1 — verdicts list empty.
    assert result.verdicts == []


def test_pipeline_identity_binding_failure_emits_x3a() -> None:
    receipts = base_receipts(run_id="")  # bind_run_identity failure
    result = run_exit_eval(receipts)
    assert result.disposition is V6Disposition.DENY
    assert any(f.reason_code == "IDENTITY_BINDING_INCOMPLETE" for f in result.preflight_failures)


def test_pipeline_can_skip_identity_binding() -> None:
    pipeline = ExitEvalPipeline(skip_identity_binding=True)
    receipts = base_receipts(run_id="")  # would normally fail identity binding
    result = pipeline.run(receipts)
    # Skipping identity binding lets the pipeline reach X1; clean ctx allows.
    assert result.disposition is V6Disposition.ALLOW


def test_pipeline_evidence_empty_emits_x3e() -> None:
    receipts = base_receipts(
        evidence_bundle={"sources": []},
        final_evidence_contract={"c0_status": "EMPTY"},
    )
    result = run_exit_eval(receipts)
    assert result.disposition is V6Disposition.SAFE_ABSTAIN
    assert isinstance(result.x3_packet, X3SafeAbstainPacket)


def test_pipeline_l4_write_attempt_emits_x3a() -> None:
    receipts = base_receipts(state_diff={"direct_l4_write_caller": "L2"})
    result = run_exit_eval(receipts)
    assert result.disposition is V6Disposition.DENY


def test_pipeline_commit_path_without_uwg_returns_packet_only() -> None:
    receipts = base_receipts(
        terminal_class="with_state_diff",
        write_intent_class="user_data_update",
        state_diff={
            "complete": True,
            "bounded": True,
            "blast_radius": "low",
            "uwg_routed": True,
        },
        capability_token={"authorizes_write": True, "expired": False},
        grader_composition={
            "roster": ["x"],
            "threshold_profile": "p",
            "consistency": {"pass_power_estimate": 0.98, "theta": 0.95, "sample_quality": "ok"},
        },
    )
    result = run_exit_eval(receipts)
    assert result.disposition is V6Disposition.COMMIT_REQUEST
    assert isinstance(result.x3_packet, X3CommitRequestPacket)
    assert result.uwg_receipt is None  # no backends -> no handoff


def test_pipeline_commit_path_with_uwg_invokes_handoff() -> None:
    receipts = base_receipts(
        terminal_class="with_state_diff",
        write_intent_class="user_data_update",
        state_diff={
            "complete": True,
            "bounded": True,
            "blast_radius": "low",
            "uwg_routed": True,
        },
        capability_token={"authorizes_write": True},
        grader_composition={
            "roster": ["x"],
            "threshold_profile": "p",
            "consistency": {"pass_power_estimate": 0.98, "theta": 0.95, "sample_quality": "ok"},
        },
    )
    backends = default_backends()
    result = run_exit_eval(receipts, uwg_backends=backends)
    assert result.disposition is V6Disposition.COMMIT_REQUEST
    assert result.uwg_receipt is not None
    assert result.uwg_receipt.outcome is UwgOutcome.COMMIT_ACCEPTED


def test_pipeline_returns_review_packet_for_introspection() -> None:
    result = run_exit_eval(base_receipts())
    assert result.packet is not None
    assert result.packet.policy_hash == "pol::v1"


def test_pipeline_rationale_field_populated() -> None:
    result = run_exit_eval(base_receipts())
    assert result.rationale  # non-empty


def test_pipeline_x3a_packet_carries_failed_field_codes() -> None:
    receipts = base_receipts(policy_hash="", replay_key="")
    result = run_exit_eval(receipts)
    pkt = result.x3_packet
    assert isinstance(pkt, X3DenyPacket)
    assert "POLICY_HASH_MISSING" in pkt.reason_codes
    assert "REPLAY_KEY_MISSING" in pkt.reason_codes
    assert pkt.user_safe_message  # non-empty
