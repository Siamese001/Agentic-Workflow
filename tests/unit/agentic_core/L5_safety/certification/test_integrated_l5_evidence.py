"""Integrated L5 evidence emission (00A parent pack)."""

from __future__ import annotations

from agentic_core.L5_safety.certification.integrated_l5_evidence import (
    build_hitl_reclearance_cleared,
    build_hitl_reclearance_not_applicable,
    build_runtime_certification_binding_payload,
)
from agentic_core.L5_safety.certification.l5_parent_vocab import (
    internal_cert_status_to_parent,
)


def test_binding_payload_parent_fields() -> None:
    payload = build_runtime_certification_binding_payload(
        request_id="req-1",
        run_id="run-1",
        trace_root="trace-1",
        policy_hash="pol-a",
        blueprint_hash="blue-b",
        registry_digest_set=("reg-1",),
        capability_token_id="cap-1",
        origin_trust_class="TRUSTED_RUNTIME",
    )
    assert payload["req_id"] == "REQ-L5-RUNTIME-BIND-001"
    assert payload["cert_status"] == "certified"
    assert payload["origin_trust_class"] == "TRUSTED_RUNTIME"
    assert payload["capability_token_id"] == "cap-1"
    assert payload["policy_hash"] == "pol-a"


def test_hitl_reclearance_cleared_human_text_as_data() -> None:
    payload = build_hitl_reclearance_cleared(
        request_id="req-1",
        run_id="run-1",
        human_response_hash="abc123",
        human_review_packet_ref="urn:hitl:packet:1",
        original_binding_ref="binding:run-1",
    )
    assert payload["human_text_treated_as_data"] is True
    assert payload["cert_status"] == "certified"
    assert payload["req_id"] == "REQ-L5-HITL-RECLEAR-001"


def test_hitl_not_applicable() -> None:
    payload = build_hitl_reclearance_not_applicable(
        request_id="req-1",
        run_id="run-1",
    )
    assert payload["not_applicable"] is True
    assert payload["human_text_treated_as_data"] is True


def test_internal_to_parent_vocab() -> None:
    assert internal_cert_status_to_parent("L5_CERTIFIED") == "certified"
    assert internal_cert_status_to_parent("L5_NOT_CERTIFIED") == "not_certified"
