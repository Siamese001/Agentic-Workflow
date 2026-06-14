"""Unit tests for agentic_core.L0_routing.u0_intake_validator.

Wave 6.1 (P2 untested-module coverage). U0 validates AppsRgIngressPayload and
emits ValidatedRequest. Covers the AuthorityValidationReceipt dataclass,
forbidden-authority-field rejection, and the validated-request stamping path.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L0_routing.u0_intake_validator import (
    AuthorityValidationReceipt,
    U0IntakeValidator,
)
from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    AppsRgIngressPayload,
    ValidatedRequest,
)


def _payload(**kw: object) -> AppsRgIngressPayload:
    base: dict[str, object] = {
        "app_id": "apps_rg",
        "task_class": "resume_generation",
        "target_company": "Acme",
        "idempotency_key": "idem-1",
        "payload_digest": "deadbeef",
        "l5_certification_ref": "cert-ref-ok",
    }
    base.update(kw)
    return AppsRgIngressPayload(**base)  # type: ignore[arg-type]


class TestAuthorityValidationReceipt:
    def test_defaults(self) -> None:
        r = AuthorityValidationReceipt(validation_timestamp="2026-01-01T00:00:00Z")
        assert r.validator_version == "W6.0"
        assert r.forbidden_fields_checked == ()
        assert r.validation_passed is True

    def test_frozen(self) -> None:
        r = AuthorityValidationReceipt(validation_timestamp="t")
        with pytest.raises(dataclasses.FrozenInstanceError):
            r.validation_passed = False  # type: ignore[misc]

    def test_slots(self) -> None:
        r = AuthorityValidationReceipt(validation_timestamp="t")
        assert not hasattr(r, "__dict__")


class TestForbiddenFields:
    def test_forbidden_field_list_is_canonical(self) -> None:
        assert U0IntakeValidator.FORBIDDEN_AUTHORITY_FIELDS == (
            "route_id",
            "execution_form",
            "provider",
            "workflow_dag",
            "llm_gateway",
            "model_endpoint",
        )

    def test_check_forbidden_fields_passes_clean_payload(self) -> None:
        # Clean payload (no authority fields) must not raise.
        U0IntakeValidator()._check_forbidden_fields(_payload())

    def test_forbidden_field_present_and_truthy_raises(self) -> None:
        # AppsRgIngressPayload has no authority slots, so inject via a stand-in
        # object exposing __dict__ with a forbidden field.
        class Stub:
            def __init__(self) -> None:
                self.route_id = "R4"

        with pytest.raises(ValueError, match="Forbidden authority field detected in ingress: route_id"):
            U0IntakeValidator()._check_forbidden_fields(Stub())  # type: ignore[arg-type]

    def test_forbidden_field_present_but_falsy_is_allowed(self) -> None:
        class Stub:
            def __init__(self) -> None:
                self.provider = ""  # falsy -> not a violation

        # Should not raise.
        U0IntakeValidator()._check_forbidden_fields(Stub())  # type: ignore[arg-type]


class TestValidate:
    def test_validate_emits_validated_request(self) -> None:
        vr = U0IntakeValidator().validate(_payload())
        assert isinstance(vr, ValidatedRequest)
        assert vr.app_id == "apps_rg"
        assert vr.task_class == "resume_generation"
        assert vr.payload_digest == "deadbeef"

    def test_validate_uses_idempotency_key_as_request_id(self) -> None:
        vr = U0IntakeValidator().validate(_payload(idempotency_key="idem-xyz"))
        assert vr.request_id == "idem-xyz"

    def test_validate_generates_request_id_when_no_idempotency_key(self) -> None:
        vr = U0IntakeValidator().validate(_payload(idempotency_key=None))
        # uuid4 hex form has dashes and is non-empty
        assert vr.request_id and "-" in vr.request_id

    def test_validate_stamps_receipt_with_forbidden_field_list(self) -> None:
        vr = U0IntakeValidator().validate(_payload())
        receipt = vr.authority_validation_receipt
        assert isinstance(receipt, AuthorityValidationReceipt)
        assert receipt.validation_passed is True
        assert receipt.forbidden_fields_checked == U0IntakeValidator.FORBIDDEN_AUTHORITY_FIELDS

    def test_validate_propagates_l5_cert_ref(self) -> None:
        vr = U0IntakeValidator().validate(_payload(l5_certification_ref="cert-abc"))
        assert vr.l5_certification_ref == "cert-abc"

    def test_validate_assigns_distinct_run_and_trace_ids(self) -> None:
        vr = U0IntakeValidator().validate(_payload())
        assert vr.run_id and vr.trace_id
        assert vr.run_id != vr.trace_id
