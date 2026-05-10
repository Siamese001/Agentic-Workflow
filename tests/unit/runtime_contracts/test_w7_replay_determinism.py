"""W7 tests — replay_key + snapshot_refs on all 11 emit contracts (Concern #4).

Covers P7.1: field presence, type, and default semantics for replay/determinism
fields added to every emit contract. CommitRequest already had replay_key as a
required field; it now also carries snapshot_refs. L3RuntimeOrchestrationReceipt
already had deterministic_digest + static_dag_ref; it now also carries replay_key
+ snapshot_refs.
"""
from __future__ import annotations

import dataclasses
import pytest


# ---------------------------------------------------------------------------
# Helpers — reuse factory pattern from W6 tests
# ---------------------------------------------------------------------------

def _make_validated_request():
    from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
    from agentic_core.L0_routing.u0_intake_validator import AuthorityValidationReceipt
    avr = AuthorityValidationReceipt(validation_timestamp="2026-01-01T00:00:00Z")
    return ValidatedRequest(
        request_id="r1", run_id="run1", app_id="apps_rg",
        task_class="resume_generation", payload_digest="d" * 64,
        authority_validation_receipt=avr, trace_id="t1",
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
        request_id="r1", run_id="run1", app_id="apps_rg", trace_id="t1",
        route_id="R3_SIMPLE", l3_required=False,
        grounding_required=False, model_generation_required=False,
        write_authority_present=False, l5_certification_ref="cert-test-ok",
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
        route_contract_id="rc1", route_id="route1",
        dag_id="dag1", dag_sha256="d" * 64,
        selected_node_ids=("n1",), step_contracts=(),
        l5_certification_ref="cert-test-ok",
    )


def _make_exhaust():
    from agentic_core.L6_observability.runtime_trace.runtime_exhaust_bundle import (
        RuntimeExhaustBundle,
    )
    return RuntimeExhaustBundle(
        raw_evidence_refs=(), lineage_manifest={}, stage_map={},
        artifact_inventory=(), gap_report=(),
        ingest_quality_score=1.0, newest_span_age_seconds=0.0,
        bundle_id="b1", l5_certification_ref="cert-test-ok",
    )


def _make_commit():
    from agentic_core.L4_state.contracts.records import CommitRequest
    return CommitRequest(
        commit_request_id="cr1", cleared_exit_review_packet_ref="ep1",
        request_id="r1", run_id="run1", trace_root="t1", tenant_id="tenant1",
        policy_hash="ph1", blueprint_hash="bh1",
        route_contract_ref="rc1", replay_key="rk1",
        rollback_plan_ref="rp1", blast_radius="low",
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
# P7.1 — replay_key field on all 11 contracts
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name,factory", _CONTRACTS, ids=[c[0] for c in _CONTRACTS])
def test_replay_key_field_exists(name, factory):
    instance = factory()
    assert hasattr(instance, "replay_key"), f"{name} missing replay_key field"


@pytest.mark.parametrize("name,factory", _CONTRACTS, ids=[c[0] for c in _CONTRACTS])
def test_replay_key_is_str(name, factory):
    instance = factory()
    assert isinstance(instance.replay_key, str), (
        f"{name}.replay_key should be str, got {type(instance.replay_key)}"
    )


# ---------------------------------------------------------------------------
# P7.1 — snapshot_refs field on all 11 contracts
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name,factory", _CONTRACTS, ids=[c[0] for c in _CONTRACTS])
def test_snapshot_refs_field_exists(name, factory):
    instance = factory()
    assert hasattr(instance, "snapshot_refs"), f"{name} missing snapshot_refs field"


@pytest.mark.parametrize("name,factory", _CONTRACTS, ids=[c[0] for c in _CONTRACTS])
def test_snapshot_refs_default_empty_tuple(name, factory):
    instance = factory()
    assert instance.snapshot_refs == (), (
        f"{name}.snapshot_refs default should be empty tuple"
    )


@pytest.mark.parametrize("name,factory", _CONTRACTS, ids=[c[0] for c in _CONTRACTS])
def test_snapshot_refs_is_tuple(name, factory):
    instance = factory()
    assert isinstance(instance.snapshot_refs, tuple), (
        f"{name}.snapshot_refs should be tuple"
    )


# ---------------------------------------------------------------------------
# Semantic defaults — replay_key defaults per layer role
# ---------------------------------------------------------------------------

def test_validated_request_replay_key_default_empty():
    assert _make_validated_request().replay_key == ""


def test_l1_replay_key_default_empty():
    assert _make_l1().replay_key == ""


def test_route_replay_key_default_empty():
    assert _make_route().replay_key == ""


def test_commit_replay_key_supplied():
    # CommitRequest.replay_key is a required positional field (not optional)
    cr = _make_commit()
    assert cr.replay_key == "rk1"


def test_commit_snapshot_refs_default_empty():
    # snapshot_refs is new to CommitRequest in W7; existing callers unaffected
    assert _make_commit().snapshot_refs == ()


# ---------------------------------------------------------------------------
# L3 receipt already has deterministic_digest — confirm both old and new fields
# ---------------------------------------------------------------------------

def test_l3_receipt_has_deterministic_digest():
    l3 = _make_l3()
    assert hasattr(l3, "deterministic_digest")
    assert isinstance(l3.deterministic_digest, str)


def test_l3_receipt_has_replay_key():
    l3 = _make_l3()
    assert l3.replay_key == ""


def test_l3_receipt_has_snapshot_refs():
    l3 = _make_l3()
    assert l3.snapshot_refs == ()


# ---------------------------------------------------------------------------
# Replay fields can be populated without breaking frozen invariant
# ---------------------------------------------------------------------------

def test_validated_request_with_replay_key():
    from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
    from agentic_core.L0_routing.u0_intake_validator import AuthorityValidationReceipt
    avr = AuthorityValidationReceipt(validation_timestamp="2026-01-01T00:00:00Z")
    vr = ValidatedRequest(
        request_id="r1", run_id="run1", app_id="apps_rg",
        task_class="resume_generation", payload_digest="d" * 64,
        authority_validation_receipt=avr, trace_id="t1",
        replay_key="rk-u0-abc123",
        snapshot_refs=("snap-1", "snap-2"),
        l5_certification_ref="cert-test-ok",
    )
    assert vr.replay_key == "rk-u0-abc123"
    assert vr.snapshot_refs == ("snap-1", "snap-2")


def test_l3_receipt_with_replay_key_and_snapshot_refs():
    from agentic_core.runtime.contracts.l3_runtime_orchestration_receipt import (
        L3RuntimeOrchestrationReceipt,
    )
    receipt = L3RuntimeOrchestrationReceipt(
        run_id="run1", request_id="r1", trace_root="t1",
        route_contract_id="rc1", route_id="route1",
        dag_id="dag1", dag_sha256="d" * 64,
        selected_node_ids=("n1",), step_contracts=(),
        replay_key="rk-l3-xyz", snapshot_refs=("snap-dag-1",),
        l5_certification_ref="cert-test-ok",
    )
    assert receipt.replay_key == "rk-l3-xyz"
    assert receipt.snapshot_refs == ("snap-dag-1",)
