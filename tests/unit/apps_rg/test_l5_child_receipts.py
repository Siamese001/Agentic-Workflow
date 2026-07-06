"""apps-test-model: LAW."""

from agentic_core.L5_safety.certification.l5_packet_producer import L5PacketProducer

from apps_rg.runtime.l5.child_receipts import build_child_certifier_receipts
from apps_rg.runtime.l5.governance_profile import load_l5_governance_profile


def _run_context(**overrides):
    base = {
        "request_id": "req-l5",
        "run_id": "run-l5",
        "trace_id": "trace-l5",
        "replay_key": "replay-l5",
        "l5_certification_ref": "l5:apps_rg:u0:valid",
    }
    base.update(overrides)
    return base


def test_child_receipts_include_required_domains_and_conditionals() -> None:
    profile = load_l5_governance_profile()
    receipts = build_child_certifier_receipts(
        profile=profile,
        run_context=_run_context(),
    )

    domains = {receipt.domain for receipt in receipts}
    assert {
        "safety_enforcement",
        "authority_context_registry_binding",
        "origin_trust_content_boundary",
        "replay_audit_certification_evidence",
        "static_governance_structure_drift",
        "runtime_certification_binding",
        "hitl_reclearance",
        "egress_provider_governance",
    } <= domains


def test_no_provider_call_emits_egress_not_applicable_triple() -> None:
    profile = load_l5_governance_profile()
    receipts = build_child_certifier_receipts(
        profile=profile,
        run_context=_run_context(),
        egress_occurred=False,
    )
    egress = next(r for r in receipts if r.domain == "egress_provider_governance")

    assert egress.applicability == "NOT_APPLICABLE"
    assert egress.not_applicable_reason
    assert egress.deciding_policy_ref
    assert egress.deciding_stage


def test_missing_replay_key_receipt_drives_packet_not_certified() -> None:
    profile = load_l5_governance_profile()
    receipts = build_child_certifier_receipts(
        profile=profile,
        run_context=_run_context(replay_key=""),
    )

    packet = L5PacketProducer().produce_packet(
        child_receipts=receipts,
        egress_receipts=(),
        certified_object_ref="urn:apps-rg:test:sealed",
        policy_ref="apps_rg/config/l0_policy.yaml",
        authority_ref="urn:apps-rg:test:authority",
        producer_ref="apps_rg.test",
    )

    assert packet.certification_status == "L5_NOT_CERTIFIED"
    assert any("missing_replay_key" in rc for rc in packet.reason_codes)


def test_placeholder_cert_ref_rejected_unless_test_flag() -> None:
    profile = load_l5_governance_profile()
    blocked = build_child_certifier_receipts(
        profile=profile,
        run_context=_run_context(l5_certification_ref="test:valid:w6"),
    )
    allowed = build_child_certifier_receipts(
        profile=profile,
        run_context=_run_context(
            l5_certification_ref="test:valid:w6",
            allow_test_l5_cert_ref=True,
        ),
    )

    blocked_runtime = next(r for r in blocked if r.domain == "runtime_certification_binding")
    allowed_runtime = next(r for r in allowed if r.domain == "runtime_certification_binding")
    assert blocked_runtime.certified is False
    assert "placeholder_l5_cert_ref_rejected" in blocked_runtime.reason_codes
    assert allowed_runtime.certified is True
