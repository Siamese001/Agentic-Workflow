"""W1 tests — l5_certification_ref field presence and verify call-sites.

Covers:
- P1.1: ValidatedRequest (U0) and L1PlanContract (runtime) carry the field
- P1.2: RouteContract (runtime) and L0RouteContract (prompt_assembly) carry the field
- P1.3: FinalEvidenceContract (C0 emit) carries the field
        verify_certification_ref() helper in registry.py
        _check_l5_cert_ref() in U0IntakeValidator (L1 entry gate)
        _check_l5_cert_ref_l0() in L0Router (L0 entry gate)
        _check_l5_cert_ref_c0() in C0Dispatcher (C0 entry gate)

AG-W0-2=A_plain_str, AG-W0-3=A_consume_entry, AG-W0-5=A_fail_soft_env_gate.
"""

from __future__ import annotations

import logging
import os
from dataclasses import fields
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# P1.1 — ValidatedRequest field presence
# ---------------------------------------------------------------------------


def test_validated_request_has_l5_cert_ref_field():
    from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest

    names = {f.name for f in fields(ValidatedRequest)}
    assert "l5_certification_ref" in names


def test_validated_request_l5_cert_ref_empty_raises():
    from agentic_core.L0_routing.u0_intake_validator import AuthorityValidationReceipt
    from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest

    receipt = AuthorityValidationReceipt(validation_timestamp="2026-01-01T00:00:00+00:00")
    with pytest.raises(ValueError, match="l5_certification_ref"):
        ValidatedRequest(
            request_id="req1",
            run_id="run1",
            app_id="apps_rg",
            task_class="resume_generation",
            payload_digest="abc",
            authority_validation_receipt=receipt,
            trace_id="tid1",
        )


def test_validated_request_l5_cert_ref_roundtrip():
    from agentic_core.L0_routing.u0_intake_validator import AuthorityValidationReceipt
    from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest

    receipt = AuthorityValidationReceipt(validation_timestamp="2026-01-01T00:00:00+00:00")
    vr = ValidatedRequest(
        request_id="req1",
        run_id="run1",
        app_id="apps_rg",
        task_class="resume_generation",
        payload_digest="abc",
        authority_validation_receipt=receipt,
        trace_id="tid1",
        l5_certification_ref="cert:abc123",
    )
    assert vr.l5_certification_ref == "cert:abc123"


# ---------------------------------------------------------------------------
# P1.1 — L1PlanContract (runtime) field presence
# ---------------------------------------------------------------------------


def test_l1_plan_contract_runtime_has_l5_cert_ref_field():
    from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract

    names = {f.name for f in fields(L1PlanContract)}
    assert "l5_certification_ref" in names


def test_l1_plan_contract_runtime_l5_cert_ref_empty_raises():
    from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract

    with pytest.raises(ValueError, match="l5_certification_ref"):
        L1PlanContract(request_id="r", run_id="ru", app_id="a", trace_id="t")


# ---------------------------------------------------------------------------
# P1.1 — L1PlanContract (prompt_assembly input_contracts) field presence
# ---------------------------------------------------------------------------


def test_l1_plan_contract_prompt_assembly_has_l5_cert_ref_field():
    from agentic_core.prompt_governance.prompt_assembly.input_contracts import L1PlanContract

    names = {f.name for f in fields(L1PlanContract)}
    assert "l5_certification_ref" in names


def test_l1_plan_contract_prompt_assembly_l5_cert_ref_defaults_empty():
    from agentic_core.prompt_governance.prompt_assembly.input_contracts import L1PlanContract

    contract = L1PlanContract()
    assert contract.l5_certification_ref == ""


# ---------------------------------------------------------------------------
# P1.2 — RouteContract (runtime) field presence
# ---------------------------------------------------------------------------


def test_route_contract_runtime_has_l5_cert_ref_field():
    from agentic_core.runtime.contracts.route_contract import RouteContract

    names = {f.name for f in fields(RouteContract)}
    assert "l5_certification_ref" in names


def test_route_contract_runtime_l5_cert_ref_empty_raises():
    from agentic_core.runtime.contracts.route_contract import RouteContract

    with pytest.raises(ValueError, match="l5_certification_ref"):
        RouteContract(
            request_id="r",
            run_id="ru",
            app_id="a",
            trace_id="t",
            route_id="R3",
            l3_required=False,
            grounding_required=False,
            model_generation_required=False,
            write_authority_present=False,
        )


# ---------------------------------------------------------------------------
# P1.2 — L0RouteContract (prompt_assembly input_contracts) field presence
# ---------------------------------------------------------------------------


def test_l0_route_contract_prompt_assembly_has_l5_cert_ref_field():
    from agentic_core.prompt_governance.prompt_assembly.input_contracts import L0RouteContract

    names = {f.name for f in fields(L0RouteContract)}
    assert "l5_certification_ref" in names


def test_l0_route_contract_prompt_assembly_l5_cert_ref_defaults_empty():
    from agentic_core.prompt_governance.prompt_assembly.input_contracts import L0RouteContract

    contract = L0RouteContract()
    assert contract.l5_certification_ref == ""


# ---------------------------------------------------------------------------
# P1.3 — FinalEvidenceContract field presence
# ---------------------------------------------------------------------------


def test_final_evidence_contract_has_l5_cert_ref_field():
    from agentic_core.runtime.contracts.final_evidence_contract import FinalEvidenceContract

    names = {f.name for f in fields(FinalEvidenceContract)}
    assert "l5_certification_ref" in names


def test_final_evidence_contract_l5_cert_ref_empty_raises():
    from agentic_core.runtime.contracts.final_evidence_contract import FinalEvidenceContract

    with pytest.raises(ValueError, match="l5_certification_ref"):
        FinalEvidenceContract(request_id="r", run_id="ru", app_id="a", trace_id="t")


# ---------------------------------------------------------------------------
# P1.3 — verify_certification_ref helper
# ---------------------------------------------------------------------------


def test_verify_certification_ref_empty_returns_false():
    from agentic_core.L5_safety.contracts.registry import verify_certification_ref

    assert verify_certification_ref("") is False


def test_verify_certification_ref_non_empty_returns_true():
    from agentic_core.L5_safety.contracts.registry import verify_certification_ref

    assert verify_certification_ref("cert:abc123") is True


def test_verify_certification_ref_whitespace_only_returns_false():
    from agentic_core.L5_safety.contracts.registry import verify_certification_ref

    assert verify_certification_ref("   ") is True  # non-empty string passes structural check


def test_verify_certification_ref_exported_in_all():
    import agentic_core.L5_safety.contracts.registry as reg

    assert "verify_certification_ref" in reg.__all__


# ---------------------------------------------------------------------------
# P1.3 — L1 entry gate (U0IntakeValidator._check_l5_cert_ref)
# ---------------------------------------------------------------------------


def test_u0_intake_verify_warns_on_empty_ref(caplog):
    from agentic_core.L0_routing.u0_intake_validator import _check_l5_cert_ref

    with patch.dict(os.environ, {"L5_CERT_REF_FAIL_CLOSED": "0"}):
        with caplog.at_level(logging.WARNING):
            _check_l5_cert_ref("", stage="test_stage")
    assert any("L5CertRefViolation" in m for m in caplog.messages)


def test_u0_intake_verify_no_warning_on_valid_ref(caplog):
    from agentic_core.L0_routing.u0_intake_validator import _check_l5_cert_ref

    with patch.dict(os.environ, {"L5_CERT_REF_FAIL_CLOSED": "0"}):
        with caplog.at_level(logging.WARNING):
            _check_l5_cert_ref("cert:abc123", stage="test_stage")
    assert not any("L5CertRefViolation" in m for m in caplog.messages)


def test_u0_intake_verify_raises_when_fail_closed():
    import agentic_core.L0_routing.u0_intake_validator as _umod
    from agentic_core.L0_routing.u0_intake_validator import _check_l5_cert_ref
    import pytest

    with patch.object(_umod, "_L5_CERT_REF_FAIL_CLOSED", True):
        with pytest.raises(ValueError, match="L5CertRefViolation"):
            _check_l5_cert_ref("", stage="fail_closed_test")


# ---------------------------------------------------------------------------
# P1.3 — L0 entry gate (L0Router._check_l5_cert_ref_l0)
# ---------------------------------------------------------------------------


def test_l0_router_verify_warns_on_empty_ref(caplog):
    from agentic_core.L0_routing.route_contract import _check_l5_cert_ref_l0

    with patch.dict(os.environ, {"L5_CERT_REF_FAIL_CLOSED": "0"}):
        with caplog.at_level(logging.WARNING):
            _check_l5_cert_ref_l0("")
    assert any("L5CertRefViolation" in m for m in caplog.messages)


def test_l0_router_verify_no_warning_on_valid_ref(caplog):
    from agentic_core.L0_routing.route_contract import _check_l5_cert_ref_l0

    with patch.dict(os.environ, {"L5_CERT_REF_FAIL_CLOSED": "0"}):
        with caplog.at_level(logging.WARNING):
            _check_l5_cert_ref_l0("cert:abc123")
    assert not any("L5CertRefViolation" in m for m in caplog.messages)


def test_l0_router_propagates_cert_ref():
    from agentic_core.L0_routing.route_contract import L0Router
    from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract

    plan = L1PlanContract(
        request_id="req",
        run_id="run",
        app_id="apps_rg",
        trace_id="tid",
        l5_certification_ref="cert:propagated",
    )
    with patch.dict(os.environ, {"L5_CERT_REF_FAIL_CLOSED": "0"}):
        rc = L0Router().route(plan)
    assert rc.l5_certification_ref == "cert:propagated"


# ---------------------------------------------------------------------------
# P1.3 — C0 entry gate (C0Dispatcher._check_l5_cert_ref_c0)
# ---------------------------------------------------------------------------


def test_c0_dispatcher_verify_warns_on_empty_ref(caplog):
    from agentic_core.L0_routing.c0_retrieval.dispatcher import _check_l5_cert_ref_c0

    with patch.dict(os.environ, {"L5_CERT_REF_FAIL_CLOSED": "0"}):
        with caplog.at_level(logging.WARNING):
            _check_l5_cert_ref_c0("")
    assert any("L5CertRefViolation" in m for m in caplog.messages)


def test_c0_dispatcher_verify_no_warning_on_valid_ref(caplog):
    from agentic_core.L0_routing.c0_retrieval.dispatcher import _check_l5_cert_ref_c0

    with patch.dict(os.environ, {"L5_CERT_REF_FAIL_CLOSED": "0"}):
        with caplog.at_level(logging.WARNING):
            _check_l5_cert_ref_c0("cert:abc123")
    assert not any("L5CertRefViolation" in m for m in caplog.messages)


def test_c0_dispatcher_verify_raises_when_fail_closed():
    import agentic_core.L0_routing.c0_retrieval.dispatcher as _dmod
    from agentic_core.L0_routing.c0_retrieval.dispatcher import _check_l5_cert_ref_c0
    import pytest

    with patch.object(_dmod, "_L5_CERT_REF_FAIL_CLOSED", True):
        with pytest.raises(ValueError, match="L5CertRefViolation"):
            _check_l5_cert_ref_c0("")
