"""W6 tests — RuntimePosture struct + gate_verdict_refs on all 11 emit contracts.

Covers:
- P6.1: RuntimePosture dataclass shape and canonical instances
- P6.2: posture field presence, type, and default on all 11 contracts
- P6.3: gate_verdict_refs field presence, type, and default on all 11 contracts
        (CommitRequest already had it from L4 vocabulary)
- Cross-cutting: default posture semantics per layer role
"""
from __future__ import annotations

import dataclasses
import pytest

from agentic_core.runtime.contracts.posture import (
    RuntimePosture,
    POSTURE_READ_ONLY,
    POSTURE_RETRIEVAL,
    POSTURE_GENERATION,
    POSTURE_WRITE_INTENT,
    POSTURE_HITL_REQUIRED,
)


# ---------------------------------------------------------------------------
# P6.1 — RuntimePosture struct shape
# ---------------------------------------------------------------------------

def test_runtime_posture_is_dataclass():
    assert dataclasses.is_dataclass(RuntimePosture)


def test_runtime_posture_is_frozen():
    p = RuntimePosture()
    with pytest.raises((dataclasses.FrozenInstanceError, TypeError)):
        p.read_only = False  # type: ignore[misc]


def test_runtime_posture_fields():
    fields = {f.name for f in dataclasses.fields(RuntimePosture)}
    assert fields == {"read_only", "external_call", "write_intent", "hitl_required", "posture_class"}


def test_runtime_posture_default_is_read_only():
    p = RuntimePosture()
    assert p.read_only is True
    assert p.external_call is False
    assert p.write_intent is False
    assert p.hitl_required is False
    assert p.posture_class == "read_only"


def test_posture_read_only_sentinel():
    assert POSTURE_READ_ONLY.read_only is True
    assert POSTURE_READ_ONLY.external_call is False
    assert POSTURE_READ_ONLY.write_intent is False
    assert POSTURE_READ_ONLY.hitl_required is False


def test_posture_retrieval_sentinel():
    assert POSTURE_RETRIEVAL.read_only is False
    assert POSTURE_RETRIEVAL.external_call is True
    assert POSTURE_RETRIEVAL.write_intent is False
    assert POSTURE_RETRIEVAL.posture_class == "retrieval"


def test_posture_generation_sentinel():
    assert POSTURE_GENERATION.external_call is True
    assert POSTURE_GENERATION.posture_class == "generation"


def test_posture_write_intent_sentinel():
    assert POSTURE_WRITE_INTENT.write_intent is True
    assert POSTURE_WRITE_INTENT.hitl_required is False
    assert POSTURE_WRITE_INTENT.posture_class == "write_intent"


def test_posture_hitl_required_sentinel():
    assert POSTURE_HITL_REQUIRED.hitl_required is True
    assert POSTURE_HITL_REQUIRED.write_intent is True


# ---------------------------------------------------------------------------
# Helpers — minimal valid constructor args per contract
# ---------------------------------------------------------------------------

def _make_validated_request():
    from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
    from agentic_core.L0_routing.u0_intake_validator import AuthorityValidationReceipt
    avr = AuthorityValidationReceipt(validation_timestamp="2026-01-01T00:00:00Z")
    return ValidatedRequest(
        request_id="r1",
        run_id="run1",
        app_id="apps_rg",
        task_class="resume_generation",
        payload_digest="d" * 64,
        authority_validation_receipt=avr,
        trace_id="t1",
        l5_certification_ref="cert-test-ok",
    )


def _make_l1():
    from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
    return L1PlanContract(
        request_id="r1", run_id="run1", app_id="apps_rg",
        trace_id="t1", l5_certification_ref="cert-test-ok",
    )


def _make_route():
    from agentic_core.runtime.contracts.route_contract import RouteContract
    return RouteContract(
        request_id="r1", run_id="run1", app_id="apps_rg",
        trace_id="t1",
        route_id="R3_SIMPLE",
        l3_required=False,
        grounding_required=False,
        model_generation_required=False,
        write_authority_present=False,
        l5_certification_ref="cert-test-ok",
    )


def _make_fec():
    from agentic_core.runtime.contracts.final_evidence_contract import FinalEvidenceContract
    return FinalEvidenceContract(
        request_id="r1", run_id="run1", app_id="apps_rg",
        trace_id="t1", l5_certification_ref="cert-test-ok",
    )


def _make_compiled():
    from agentic_core.runtime.contracts.compiled_prompt_artifact import CompiledPromptArtifact
    return CompiledPromptArtifact(
        request_id="r1", run_id="run1", app_id="apps_rg",
        trace_id="t1", target_model="test-model",
        l5_certification_ref="cert-test-ok",
    )


def _make_sealed():
    from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
    return SealedL2Artifact(
        request_id="r1", run_id="run1", app_id="apps_rg",
        trace_id="t1", execution_status="completed",
        l5_certification_ref="cert-test-ok",
    )


def _make_x3():
    from agentic_core.runtime.contracts.x3_disposition import X3Disposition
    return X3Disposition(
        request_id="r1", run_id="run1", app_id="apps_rg",
        trace_id="t1", exit_status="success",
        l5_certification_ref="cert-test-ok",
    )


def _make_l3():
    from agentic_core.runtime.contracts.l3_runtime_orchestration_receipt import (
        L3RuntimeOrchestrationReceipt,
    )
    return L3RuntimeOrchestrationReceipt(
        run_id="run1", request_id="r1", trace_root="t1",
        route_contract_id="rc1",
        route_id="route1", dag_id="dag1", dag_sha256="d" * 64,
        selected_node_ids=("n1",),
        step_contracts=(),
        l5_certification_ref="cert-test-ok",
    )


def _make_exhaust():
    from agentic_core.L6_observability.runtime_trace.runtime_exhaust_bundle import (
        RuntimeExhaustBundle,
    )
    return RuntimeExhaustBundle(
        raw_evidence_refs=(),
        lineage_manifest={}, stage_map={},
        artifact_inventory=(), gap_report=(),
        ingest_quality_score=1.0,
        newest_span_age_seconds=0.0,
        bundle_id="b1",
        l5_certification_ref="cert-test-ok",
    )


def _make_commit():
    from agentic_core.L4_state.contracts.records import CommitRequest
    return CommitRequest(
        commit_request_id="cr1",
        cleared_exit_review_packet_ref="ep1",
        request_id="r1",
        run_id="run1",
        trace_root="t1",
        tenant_id="tenant1",
        policy_hash="ph1",
        blueprint_hash="bh1",
        route_contract_ref="rc1",
        replay_key="rk1",
        rollback_plan_ref="rp1",
        blast_radius="low",
        l5_certification_ref="cert-test-ok",
    )


_CONTRACTS = [
    ("ValidatedRequest", _make_validated_request),
    ("L1PlanContract", _make_l1),
    ("RouteContract", _make_route),
    ("FinalEvidenceContract", _make_fec),
    ("CompiledPromptArtifact", _make_compiled),
    ("SealedL2Artifact", _make_sealed),
    ("X3Disposition", _make_x3),
    ("L3RuntimeOrchestrationReceipt", _make_l3),
    ("RuntimeExhaustBundle", _make_exhaust),
    ("CommitRequest", _make_commit),
]


# ---------------------------------------------------------------------------
# P6.2 — posture field present on all 11 contracts
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name,factory", _CONTRACTS, ids=[c[0] for c in _CONTRACTS])
def test_posture_field_exists(name, factory):
    instance = factory()
    assert hasattr(instance, "posture"), f"{name} missing posture field"


@pytest.mark.parametrize("name,factory", _CONTRACTS, ids=[c[0] for c in _CONTRACTS])
def test_posture_is_runtime_posture_instance(name, factory):
    instance = factory()
    assert isinstance(instance.posture, RuntimePosture), (
        f"{name}.posture should be RuntimePosture, got {type(instance.posture)}"
    )


# ---------------------------------------------------------------------------
# P6.3 — gate_verdict_refs field present on all 11 contracts
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name,factory", _CONTRACTS, ids=[c[0] for c in _CONTRACTS])
def test_gate_verdict_refs_field_exists(name, factory):
    instance = factory()
    assert hasattr(instance, "gate_verdict_refs"), f"{name} missing gate_verdict_refs field"


@pytest.mark.parametrize("name,factory", _CONTRACTS, ids=[c[0] for c in _CONTRACTS])
def test_gate_verdict_refs_default_empty_tuple(name, factory):
    instance = factory()
    assert instance.gate_verdict_refs == (), (
        f"{name}.gate_verdict_refs default should be empty tuple"
    )


@pytest.mark.parametrize("name,factory", _CONTRACTS, ids=[c[0] for c in _CONTRACTS])
def test_gate_verdict_refs_is_tuple(name, factory):
    instance = factory()
    assert isinstance(instance.gate_verdict_refs, tuple), (
        f"{name}.gate_verdict_refs should be tuple"
    )


# ---------------------------------------------------------------------------
# Semantic defaults — posture values match expected layer role
# ---------------------------------------------------------------------------

def test_validated_request_posture_is_read_only():
    assert _make_validated_request().posture == POSTURE_READ_ONLY


def test_l1_posture_is_read_only():
    assert _make_l1().posture == POSTURE_READ_ONLY


def test_route_posture_is_read_only():
    assert _make_route().posture == POSTURE_READ_ONLY


def test_fec_posture_is_read_only():
    assert _make_fec().posture == POSTURE_READ_ONLY


def test_compiled_posture_is_generation():
    assert _make_compiled().posture == POSTURE_GENERATION


def test_sealed_posture_is_write_intent():
    assert _make_sealed().posture == POSTURE_WRITE_INTENT


def test_x3_posture_is_write_intent():
    assert _make_x3().posture == POSTURE_WRITE_INTENT


def test_l3_posture_is_read_only():
    assert _make_l3().posture == POSTURE_READ_ONLY


def test_exhaust_posture_is_read_only():
    assert _make_exhaust().posture == POSTURE_READ_ONLY


def test_commit_request_posture_is_write_intent():
    assert _make_commit().posture == POSTURE_WRITE_INTENT
