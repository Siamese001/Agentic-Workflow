"""W2 tests — l5_certification_ref field presence and verify call-sites for PA/L3/L2/X3 contracts.

Covers:
- CompiledPromptArtifact (PA emit)
- L3StepContract (L3 emit)
- SealedL2Artifact (L2 emit)
- X3DenyPacket, X3EscalatePacket, X3CommitRequestPacket, X3AllowPacket,
  X3SafeAbstainPacket, X3BreakGlassAllowPacket (Exit X3 packets)
- _check_l5_cert_ref_pa / _check_l5_cert_ref_l3 / _check_l5_cert_ref_l2 helpers
- PA pipeline entry verify gate
- L3 engine entry verify gate
- L2 executor entry verify gate
"""
from __future__ import annotations

import dataclasses
import logging
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# CompiledPromptArtifact
# ---------------------------------------------------------------------------

def test_compiled_prompt_artifact_has_l5_cert_ref_field():
    from agentic_core.runtime.contracts.compiled_prompt_artifact import CompiledPromptArtifact
    assert "l5_certification_ref" in {f.name for f in dataclasses.fields(CompiledPromptArtifact)}


def test_compiled_prompt_artifact_l5_cert_ref_empty_raises():
    from agentic_core.runtime.contracts.compiled_prompt_artifact import CompiledPromptArtifact
    with pytest.raises(ValueError, match="l5_certification_ref"):
        CompiledPromptArtifact(request_id="r", run_id="u", app_id="a", trace_id="t")


def test_compiled_prompt_artifact_l5_cert_ref_roundtrip():
    from agentic_core.runtime.contracts.compiled_prompt_artifact import CompiledPromptArtifact
    a = CompiledPromptArtifact(request_id="r", run_id="u", app_id="a", trace_id="t",
                                l5_certification_ref="cert-pa-001")
    assert a.l5_certification_ref == "cert-pa-001"


# ---------------------------------------------------------------------------
# L3StepContract
# ---------------------------------------------------------------------------

def _make_step_contract(**kwargs):
    from agentic_core.L3_orchestration.doctrine.contracts_l3_7 import L3StepContract, StepInputs
    from agentic_core.L3_orchestration.doctrine.contracts_l3_6 import WorkflowNodeType
    defaults = dict(
        step_contract_id="sc1", workflow_id="wf1", node_id="n1", attempt_id="a1",
        parent_route_id="r1", route_digest="d1", policy_hash="p1", blueprint_hash="b1",
        snapshot_id="s1", replay_key="rk1", idempotency_key="ik1",
        node_type=WorkflowNodeType.C0_GROUNDING_STEP,
        current_work_order="wo1",
        inputs=StepInputs(query_refs=("c1",)),
        expected_output_contract="oc1",
        capability_token_requirement="ct1",
        sandbox_envelope_requirement="se1",
        timeout_ms=1000,
        retry_policy="rp1",
        fallback_permission="fp1",
        telemetry_keys=("t1",),
        expected_receipts=("er1",),
        step_contract_hash="sh1",
    )
    defaults.update(kwargs)
    return L3StepContract(**defaults)


def test_l3_step_contract_has_l5_cert_ref_field():
    from agentic_core.L3_orchestration.doctrine.contracts_l3_7 import L3StepContract
    assert "l5_certification_ref" in {f.name for f in dataclasses.fields(L3StepContract)}


def test_l3_step_contract_l5_cert_ref_defaults_empty():
    sc = _make_step_contract()
    assert sc.l5_certification_ref == ""


def test_l3_step_contract_l5_cert_ref_roundtrip():
    sc = _make_step_contract(l5_certification_ref="cert-l3-001")
    assert sc.l5_certification_ref == "cert-l3-001"


# ---------------------------------------------------------------------------
# SealedL2Artifact
# ---------------------------------------------------------------------------

def test_sealed_l2_artifact_has_l5_cert_ref_field():
    from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
    assert "l5_certification_ref" in {f.name for f in dataclasses.fields(SealedL2Artifact)}


def test_sealed_l2_artifact_l5_cert_ref_empty_raises():
    from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
    with pytest.raises(ValueError, match="l5_certification_ref"):
        SealedL2Artifact(request_id="r", run_id="u", app_id="a", trace_id="t",
                         execution_status="completed")


def test_sealed_l2_artifact_l5_cert_ref_roundtrip():
    from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
    a = SealedL2Artifact(request_id="r", run_id="u", app_id="a", trace_id="t",
                          execution_status="completed", l5_certification_ref="cert-l2-001")
    assert a.l5_certification_ref == "cert-l2-001"


# ---------------------------------------------------------------------------
# X3 packet variants
# ---------------------------------------------------------------------------

def test_x3_deny_packet_has_l5_cert_ref_field():
    from agentic_core.L3_orchestration.exit_eval.v6.types import X3DenyPacket
    assert "l5_certification_ref" in {f.name for f in dataclasses.fields(X3DenyPacket)}


def test_x3_deny_packet_l5_cert_ref_empty_raises():
    from agentic_core.L3_orchestration.exit_eval.v6.types import X3DenyPacket
    with pytest.raises(ValueError, match="l5_certification_ref"):
        X3DenyPacket()


def test_x3_escalate_packet_has_l5_cert_ref_field():
    from agentic_core.L3_orchestration.exit_eval.v6.types import X3EscalatePacket
    assert "l5_certification_ref" in {f.name for f in dataclasses.fields(X3EscalatePacket)}


def test_x3_escalate_packet_l5_cert_ref_empty_raises():
    from agentic_core.L3_orchestration.exit_eval.v6.types import X3EscalatePacket
    with pytest.raises(ValueError, match="l5_certification_ref"):
        X3EscalatePacket()


def test_x3_commit_request_packet_has_l5_cert_ref_field():
    from agentic_core.L3_orchestration.exit_eval.v6.types import X3CommitRequestPacket
    assert "l5_certification_ref" in {f.name for f in dataclasses.fields(X3CommitRequestPacket)}


def test_x3_commit_request_packet_l5_cert_ref_empty_raises():
    from agentic_core.L3_orchestration.exit_eval.v6.types import X3CommitRequestPacket
    with pytest.raises(ValueError, match="l5_certification_ref"):
        X3CommitRequestPacket()


def test_x3_allow_packet_has_l5_cert_ref_field():
    from agentic_core.L3_orchestration.exit_eval.v6.types import X3AllowPacket
    assert "l5_certification_ref" in {f.name for f in dataclasses.fields(X3AllowPacket)}


def test_x3_allow_packet_l5_cert_ref_empty_raises():
    from agentic_core.L3_orchestration.exit_eval.v6.types import X3AllowPacket
    with pytest.raises(ValueError, match="l5_certification_ref"):
        X3AllowPacket()


def test_x3_safe_abstain_packet_has_l5_cert_ref_field():
    from agentic_core.L3_orchestration.exit_eval.v6.types import X3SafeAbstainPacket
    assert "l5_certification_ref" in {f.name for f in dataclasses.fields(X3SafeAbstainPacket)}


def test_x3_safe_abstain_packet_l5_cert_ref_empty_raises():
    from agentic_core.L3_orchestration.exit_eval.v6.types import X3SafeAbstainPacket
    with pytest.raises(ValueError, match="l5_certification_ref"):
        X3SafeAbstainPacket()


def test_x3_break_glass_allow_packet_has_l5_cert_ref_field():
    from agentic_core.L3_orchestration.exit_eval.v6.types import X3BreakGlassAllowPacket
    assert "l5_certification_ref" in {f.name for f in dataclasses.fields(X3BreakGlassAllowPacket)}


def test_x3_break_glass_allow_packet_l5_cert_ref_empty_raises():
    from agentic_core.L3_orchestration.exit_eval.v6.types import X3BreakGlassAllowPacket
    with pytest.raises(ValueError, match="l5_certification_ref"):
        X3BreakGlassAllowPacket()


# ---------------------------------------------------------------------------
# _check_l5_cert_ref_pa helper
# ---------------------------------------------------------------------------

def test_pa_verify_warns_on_empty_ref(caplog):
    import agentic_core.prompt_governance.prompt_assembly.pipeline as pipeline_mod
    with caplog.at_level(logging.WARNING, logger=pipeline_mod._logger.name):
        pipeline_mod._check_l5_cert_ref_pa("")
    assert any("L5CertRefViolation" in r.message and "PA_entry" in r.message
               for r in caplog.records)


def test_pa_verify_no_warning_on_valid_ref(caplog):
    import agentic_core.prompt_governance.prompt_assembly.pipeline as pipeline_mod
    with caplog.at_level(logging.WARNING, logger=pipeline_mod._logger.name):
        pipeline_mod._check_l5_cert_ref_pa("cert-pa-001")
    assert not any("L5CertRefViolation" in r.message for r in caplog.records)


def test_pa_verify_raises_when_fail_closed():
    import agentic_core.prompt_governance.prompt_assembly.pipeline as pipeline_mod
    with patch.object(pipeline_mod, "_L5_CERT_REF_FAIL_CLOSED", True):
        with pytest.raises(ValueError, match="L5CertRefViolation"):
            pipeline_mod._check_l5_cert_ref_pa("")


# ---------------------------------------------------------------------------
# _check_l5_cert_ref_l3 helper
# ---------------------------------------------------------------------------

def test_l3_verify_warns_on_empty_ref(caplog):
    import agentic_core.L3_orchestration.managed_workflow_router as mwr_mod
    with caplog.at_level(logging.WARNING, logger=mwr_mod._logger.name):
        mwr_mod._check_l5_cert_ref_l3("")
    assert any("L5CertRefViolation" in r.message and "L3_entry" in r.message
               for r in caplog.records)


def test_l3_verify_no_warning_on_valid_ref(caplog):
    import agentic_core.L3_orchestration.managed_workflow_router as mwr_mod
    with caplog.at_level(logging.WARNING, logger=mwr_mod._logger.name):
        mwr_mod._check_l5_cert_ref_l3("cert-l3-001")
    assert not any("L5CertRefViolation" in r.message for r in caplog.records)


def test_l3_verify_raises_when_fail_closed():
    import agentic_core.L3_orchestration.managed_workflow_router as mwr_mod
    with patch.object(mwr_mod, "_L5_CERT_REF_FAIL_CLOSED", True):
        with pytest.raises(ValueError, match="L5CertRefViolation"):
            mwr_mod._check_l5_cert_ref_l3("")


# ---------------------------------------------------------------------------
# _check_l5_cert_ref_l2 helper
# ---------------------------------------------------------------------------

def test_l2_verify_warns_on_empty_ref(caplog):
    import agentic_core.L2_execution.l2_execution_contract as l2_mod
    with caplog.at_level(logging.WARNING, logger=l2_mod._logger.name):
        l2_mod._check_l5_cert_ref_l2("")
    assert any("L5CertRefViolation" in r.message and "L2_entry" in r.message
               for r in caplog.records)


def test_l2_verify_no_warning_on_valid_ref(caplog):
    import agentic_core.L2_execution.l2_execution_contract as l2_mod
    with caplog.at_level(logging.WARNING, logger=l2_mod._logger.name):
        l2_mod._check_l5_cert_ref_l2("cert-l2-001")
    assert not any("L5CertRefViolation" in r.message for r in caplog.records)


def test_l2_verify_raises_when_fail_closed():
    import agentic_core.L2_execution.l2_execution_contract as l2_mod
    with patch.object(l2_mod, "_L5_CERT_REF_FAIL_CLOSED", True):
        with pytest.raises(ValueError, match="L5CertRefViolation"):
            l2_mod._check_l5_cert_ref_l2("")


# ---------------------------------------------------------------------------
# L2Executor propagates ref into SealedL2Artifact
# ---------------------------------------------------------------------------

def test_l2_executor_propagates_cert_ref():
    from agentic_core.L2_execution.l2_execution_contract import L2Executor
    from agentic_core.runtime.contracts.compiled_prompt_artifact import CompiledPromptArtifact
    from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
    from agentic_core.L0_routing.u0_intake_validator import AuthorityValidationReceipt
    receipt = AuthorityValidationReceipt(validation_timestamp="2026-01-01T00:00:00")
    vr = ValidatedRequest(request_id="r1", run_id="u1", app_id="apps_rg",
                           task_class="resume_generation", payload_digest="pd1",
                           authority_validation_receipt=receipt, trace_id="tr1",
                           l5_certification_ref="cert-prop-001")
    pa = CompiledPromptArtifact(request_id="r1", run_id="u1", app_id="apps_rg",
                                  trace_id="tr1", l5_certification_ref="cert-prop-001")
    result = L2Executor().execute(vr, pa)
    assert result.l5_certification_ref == "cert-prop-001"
