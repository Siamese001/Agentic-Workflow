"""Edge cases and fail-closed paths for integrated L5 evidence (00A parent pack)."""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.certification.integrated_l5_evidence import (
    binding_payload_from_identity,
    build_hitl_reclearance_cleared,
    build_hitl_reclearance_not_applicable,
    build_runtime_certification_binding_payload,
    certification_ref_from_binding,
)
from agentic_core.L5_safety.certification.l5_parent_vocab import (
    internal_cert_status_to_parent,
    parent_cert_status_to_internal,
)


class TestCertificationRefFailClosed:
    def test_missing_binding_id_raises(self) -> None:
        with pytest.raises(ValueError, match="binding_id"):
            certification_ref_from_binding({})

    def test_empty_binding_id_raises(self) -> None:
        with pytest.raises(ValueError, match="binding_id"):
            certification_ref_from_binding({"binding_id": ""})

    def test_whitespace_binding_id_raises(self) -> None:
        with pytest.raises(ValueError, match="binding_id"):
            certification_ref_from_binding({"binding_id": "   "})

    def test_valid_ref_is_stable_and_namespaced(self) -> None:
        payload = build_runtime_certification_binding_payload(
            request_id="req-edge",
            run_id="run-edge",
            trace_root="trace-edge",
            policy_hash="ph",
            blueprint_hash="bh",
            registry_digest_set=("reg-a",),
        )
        ref = certification_ref_from_binding(payload)
        assert ref == f"l5:runtime_certification_binding:{payload['binding_id']}"
        assert certification_ref_from_binding(payload) == ref


class TestBindingFromIdentityEdgeCases:
    def test_registry_digest_set_as_dict_values(self) -> None:
        identity = {
            "request_id": "req-dict",
            "run_id": "run-dict",
            "trace_root": "trace-dict",
            "policy_hash": "ph-d",
            "blueprint_hash": "bh-d",
            "registry_digest_set": {"a": "digest-a", "b": "digest-b"},
        }
        payload = binding_payload_from_identity(identity)
        assert sorted(payload["registry_digest_set"]) == ["digest-a", "digest-b"]

    def test_empty_registry_defaults_to_none_token(self) -> None:
        identity = {
            "request_id": "req-empty-reg",
            "run_id": "run-empty-reg",
            "trace_root": "trace-empty-reg",
            "policy_hash": "ph",
            "blueprint_hash": "bh",
            "registry_digest_set": [],
        }
        payload = binding_payload_from_identity(identity)
        assert payload["registry_digest_set"] == ["registry:none"]

    def test_run_id_falls_back_to_request_id(self) -> None:
        identity = {
            "request_id": "req-only",
            "trace_root": "",
            "policy_hash": "",
            "blueprint_hash": "",
        }
        payload = binding_payload_from_identity(identity)
        assert payload["run_id"] == "req-only"
        assert payload["trace_root"] == "req-only"

    def test_requires_reclearance_maps_to_pending_reclearance(self) -> None:
        payload = binding_payload_from_identity(
            {"request_id": "r1", "run_id": "r1", "trace_root": "t1"},
            certification_status="L5_REQUIRES_RECLEARANCE",
        )
        assert payload["cert_status"] == "pending_reclearance"


class TestHitlReclearanceEdgeCases:
    def test_not_applicable_always_marks_human_text_as_data(self) -> None:
        payload = build_hitl_reclearance_not_applicable(
            request_id="req-na",
            run_id="run-na",
            reason_code="CUSTOM_NA",
        )
        assert payload["human_text_treated_as_data"] is True
        assert payload["not_applicable"] is True
        assert payload["reason_codes"] == ["CUSTOM_NA"]
        assert payload["cert_status"] == "not_certified"
        assert payload["reclearance_binding"]["reclearance_status"] == "REQUIRES_RE_REVIEW"

    def test_cleared_requires_human_hash(self) -> None:
        payload = build_hitl_reclearance_cleared(
            request_id="req-c",
            run_id="run-c",
            human_response_hash="deadbeef",
            human_review_packet_ref="urn:hitl:1",
            original_binding_ref="binding:run-c",
            replay_key="rk-c",
        )
        assert payload["cert_status"] == "certified"
        assert payload["human_response_hash"] == "deadbeef"
        assert payload["reclearance_binding"]["reclearance_status"] == "CLEARED"
        assert payload["replay_key"] == "rk-c"


class TestParentVocabEdgeCases:
    def test_unknown_internal_status_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown internal"):
            internal_cert_status_to_parent("L5_BOGUS")

    def test_parent_token_passthrough_when_already_parent_form(self) -> None:
        assert internal_cert_status_to_parent("certified") == "certified"

    def test_invalid_parent_token_raises(self) -> None:
        with pytest.raises(ValueError, match="not in"):
            parent_cert_status_to_internal("bogus_parent")

    def test_round_trip_certified(self) -> None:
        assert parent_cert_status_to_internal(
            internal_cert_status_to_parent("L5_CERTIFIED")
        ) == "L5_CERTIFIED"
