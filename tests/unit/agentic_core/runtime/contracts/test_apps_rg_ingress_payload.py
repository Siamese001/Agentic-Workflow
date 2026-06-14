"""Unit tests for agentic_core.runtime.contracts.apps_rg_ingress_payload.

W1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — Core P1 runtime-contract surface.
``apps_rg_ingress_payload`` is the highest-fan-in untested contract (fan_in=79,
L_RUNTIME): the sole ingress shape apps_rg may produce and the input every U0
validation path consumes. Frozen, slotted dataclasses — exhaustive contract coverage.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    AppsRgIngressPayload,
    RequestEnvelope,
    ValidatedRequest,
)
from agentic_core.runtime.contracts.posture import POSTURE_READ_ONLY, RuntimePosture


class TestAppsRgIngressPayloadDefaults:
    def test_identity_defaults(self) -> None:
        p = AppsRgIngressPayload(target_company="Acme")
        assert p.app_id == "apps_rg"
        assert p.task_class == "resume_generation"

    def test_optional_fields_default_none(self) -> None:
        p = AppsRgIngressPayload(target_company="Acme")
        assert p.target_role is None
        assert p.target_level is None
        assert p.source_resume_ref is None
        assert p.source_resume_text is None
        assert p.job_description_ref is None
        assert p.briefing_artifact_ref is None
        assert p.idempotency_key is None
        assert p.l5_certification_ref is None

    def test_collection_fields_default_empty(self) -> None:
        p = AppsRgIngressPayload(target_company="Acme")
        assert p.project_fact_refs == ()
        assert p.user_constraints == {}
        assert p.output_preferences == {}

    def test_research_flags_default_false(self) -> None:
        p = AppsRgIngressPayload(target_company="Acme")
        assert p.auto_research_internal is False
        assert p.auto_research_tavily is False
        assert p.research_via is None

    def test_payload_digest_defaults_empty(self) -> None:
        assert AppsRgIngressPayload(target_company="Acme").payload_digest == ""


class TestAppsRgIngressPayloadInvariant:
    """__post_init__: needs (target_company | target_role) OR (source_resume_ref | _text)."""

    def test_target_company_only_ok(self) -> None:
        assert AppsRgIngressPayload(target_company="Acme").target_company == "Acme"

    def test_target_role_only_ok(self) -> None:
        assert AppsRgIngressPayload(target_role="SVP").target_role == "SVP"

    def test_source_resume_ref_only_ok(self) -> None:
        p = AppsRgIngressPayload(source_resume_ref="/tmp/resume.json")
        assert p.target_company is None and p.source_resume_ref == "/tmp/resume.json"

    def test_source_resume_text_only_ok(self) -> None:
        p = AppsRgIngressPayload(source_resume_text="John Doe ...")
        assert p.source_resume_text == "John Doe ..."

    def test_no_context_raises(self) -> None:
        with pytest.raises(ValueError, match="at least one of"):
            AppsRgIngressPayload()

    def test_empty_strings_count_as_missing(self) -> None:
        # Falsy target + falsy resume → invariant fails.
        with pytest.raises(ValueError, match="at least one of"):
            AppsRgIngressPayload(target_company="", target_role="", source_resume_ref="")


class TestAppsRgIngressPayloadImmutability:
    def test_frozen(self) -> None:
        p = AppsRgIngressPayload(target_company="Acme")
        with pytest.raises(dataclasses.FrozenInstanceError):
            p.target_company = "Other"  # type: ignore[misc]

    def test_slots_no_dict(self) -> None:
        # slots=True → instances have no __dict__.
        assert not hasattr(AppsRgIngressPayload(target_company="Acme"), "__dict__")


class TestRequestEnvelope:
    def test_wraps_payload(self) -> None:
        payload = AppsRgIngressPayload(target_company="Acme")
        env = RequestEnvelope(payload=payload)
        assert env.payload is payload

    def test_metadata_defaults_empty(self) -> None:
        env = RequestEnvelope(payload=AppsRgIngressPayload(target_company="Acme"))
        assert env.request_id == ""
        assert env.run_id == ""
        assert env.tenant_id == ""
        assert env.trace_id == ""
        assert env.submitted_at == ""
        assert env.replay_key == ""

    def test_frozen(self) -> None:
        env = RequestEnvelope(payload=AppsRgIngressPayload(target_company="Acme"))
        with pytest.raises(dataclasses.FrozenInstanceError):
            env.request_id = "r1"  # type: ignore[misc]


def _valid_validated_request(**overrides: object) -> ValidatedRequest:
    base: dict[str, object] = dict(
        request_id="req-1",
        run_id="run-1",
        app_id="apps_rg",
        task_class="resume_generation",
        payload_digest="deadbeef",
        authority_validation_receipt=object(),  # not validated in __post_init__
        trace_id="trace-1",
        l5_certification_ref="cert-ref-1",
    )
    base.update(overrides)
    return ValidatedRequest(**base)  # type: ignore[arg-type]


class TestValidatedRequest:
    def test_valid_construction(self) -> None:
        vr = _valid_validated_request()
        assert vr.request_id == "req-1"
        assert vr.app_id == "apps_rg"
        assert vr.l5_certification_ref == "cert-ref-1"

    def test_defaults(self) -> None:
        vr = _valid_validated_request()
        assert vr.tenant_id == ""
        assert vr.target_level == ""
        assert vr.schema_version == "W6.0"
        assert vr.signature == ""
        assert vr.otel_span_refs == ()
        assert vr.audit_refs == ()
        assert vr.gate_verdict_refs == ()
        assert vr.snapshot_refs == ()
        assert vr.app_payload == {}
        assert vr.reflection_receipt is None
        assert vr.session_id == ""

    def test_posture_default_is_read_only(self) -> None:
        vr = _valid_validated_request()
        assert isinstance(vr.posture, RuntimePosture)
        assert vr.posture == POSTURE_READ_ONLY

    def test_missing_cert_ref_raises(self) -> None:
        with pytest.raises(ValueError, match="l5_certification_ref"):
            _valid_validated_request(l5_certification_ref=None)

    @pytest.mark.parametrize("bad", ["", "   ", "\t"])
    def test_blank_cert_ref_raises(self, bad: str) -> None:
        with pytest.raises(ValueError, match="l5_certification_ref"):
            _valid_validated_request(l5_certification_ref=bad)

    def test_frozen(self) -> None:
        vr = _valid_validated_request()
        with pytest.raises(dataclasses.FrozenInstanceError):
            vr.request_id = "x"  # type: ignore[misc]
