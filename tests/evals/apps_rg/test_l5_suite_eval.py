"""apps-test-model: EVAL."""
from __future__ import annotations

import pytest

from agentic_core.L5_safety.certification.l5_packet_producer import L5PacketProducer
from agentic_core.L5_safety.contracts.l5_certification_contracts import (
    ChildCertifierReceipt,
)
from agentic_core.L5_safety.exceptions import L5DigestMismatchError
from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
from apps_rg.runtime.bindings.exit_binding import exit_finalize_apps_rg
from apps_rg.runtime.l5.packet_builder import build_l5_certification_packet

pytestmark = pytest.mark.apps_test_model("EVAL")

_REQUIRED_DOMAINS = (
    "safety_enforcement",
    "authority_context_registry_binding",
    "origin_trust_content_boundary",
    "replay_audit_certification_evidence",
    "static_governance_structure_drift",
    "runtime_certification_binding",
)
_COMMON_PACKET_REFS = {
    "certified_object_ref": "urn:apps-rg:eval:object",
    "policy_ref": "urn:apps-rg:eval:policy",
    "producer_ref": "apps_rg.eval:v1",
}


def _child(domain: str, **overrides: object) -> ChildCertifierReceipt:
    values = {
        "domain": domain,
        "applicability": "REQUIRED",
        "certified": True,
    }
    values.update(overrides)
    return ChildCertifierReceipt(**values)


def _sealed(**overrides: object) -> SealedL2Artifact:
    values = {
        "request_id": "req-suite-eval",
        "run_id": "run-suite-eval",
        "app_id": "apps_rg",
        "trace_id": "trace-suite-eval",
        "execution_status": "completed",
        "generated_content": "{}",
        "compilation_hash": "a" * 64,
        "replay_key": "replay-suite-eval",
        "l5_certification_ref": "l5:apps_rg:u0:suite-eval",
    }
    values.update(overrides)
    return SealedL2Artifact(**values)


def test_micro_unknown_child_never_passes() -> None:
    children = [_child(domain) for domain in _REQUIRED_DOMAINS]
    children[0] = _child("safety_enforcement", certified=False)

    packet = L5PacketProducer().produce_packet(
        child_receipts=children,
        egress_receipts=[],
        **_COMMON_PACKET_REFS,
    )

    assert packet.certification_status == "L5_NOT_CERTIFIED"
    assert any("UNKNOWN child" in reason for reason in packet.reason_codes)


def test_micro_missing_required_child_is_not_certified() -> None:
    packet = L5PacketProducer().produce_packet(
        child_receipts=[_child(_REQUIRED_DOMAINS[0])],
        egress_receipts=[],
        **_COMMON_PACKET_REFS,
    )

    assert packet.certification_status == "L5_NOT_CERTIFIED"
    assert any("missing required child category" in reason for reason in packet.reason_codes)


def test_micro_context_digest_mismatch_fails_closed() -> None:
    children = [_child(domain) for domain in _REQUIRED_DOMAINS]
    children[0] = _child(
        "safety_enforcement",
        l5_governance_context_digest="f" * 64,
    )

    with pytest.raises(L5DigestMismatchError):
        L5PacketProducer().produce_packet(
            child_receipts=children,
            egress_receipts=[],
            **_COMMON_PACKET_REFS,
        )


def test_micro_not_applicable_missing_triple_rejected() -> None:
    with pytest.raises(ValueError, match="NOT_APPLICABLE"):
        ChildCertifierReceipt(
            domain="hitl_reclearance",
            applicability="NOT_APPLICABLE",
            certified=True,
        )


def test_micro_placeholder_cert_ref_rejected() -> None:
    result = build_l5_certification_packet(
        sealed=_sealed(l5_certification_ref="test:valid:w6")
    )

    assert result.status == "L5_NOT_CERTIFIED"
    assert any("placeholder_l5_cert_ref_rejected" in code for code in result.packet.reason_codes)


def test_suite_eval_blocks_allow_when_l5_not_certified_and_pass_rate_is_promotion_safe() -> None:
    scenarios: list[tuple[str, bool]] = []

    missing_packet = exit_finalize_apps_rg(_sealed(), fec=None)
    scenarios.append(("missing_packet_blocks", not missing_packet.disposition.outcome_authorized))

    not_certified = exit_finalize_apps_rg(
        _sealed(
            l5_certification_packet_ref="l5_packet:not-certified",
            l5_certification_packet_digest="b" * 64,
            l5_certification_status="L5_NOT_CERTIFIED",
        ),
        fec=None,
    )
    scenarios.append(("not_certified_blocks", not not_certified.disposition.outcome_authorized))

    malformed_digest = exit_finalize_apps_rg(
        _sealed(
            l5_certification_packet_ref="l5_packet:bad-digest",
            l5_certification_packet_digest="not-a-digest",
            l5_certification_status="L5_CERTIFIED",
        ),
        fec=None,
    )
    scenarios.append(("malformed_digest_blocks", not malformed_digest.disposition.outcome_authorized))

    placeholder = exit_finalize_apps_rg(
        _sealed(
            l5_certification_ref="test:valid:w6",
            l5_certification_packet_ref="l5_packet:placeholder",
            l5_certification_packet_digest="c" * 64,
            l5_certification_status="L5_CERTIFIED",
        ),
        fec=None,
    )
    scenarios.append(("placeholder_blocks", not placeholder.disposition.outcome_authorized))

    certified = build_l5_certification_packet(sealed=_sealed())
    scenarios.append(("certified_packet_builds", certified.status == "L5_CERTIFIED"))

    pass_rate = sum(1 for _, passed in scenarios if passed) / len(scenarios)

    assert pass_rate >= 0.98, scenarios
