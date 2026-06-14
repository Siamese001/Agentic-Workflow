"""Unit tests for apps_lic.runtime.bindings.l3_binding.

Wave 4.1 — plan adg-testing-hotspots-wave-plan-a7f3c1
Module fan-in: 39.

Purpose: cover the deterministic L3 orchestration binding — the module
topology constants, the pure digest/derivation helpers
(_derive_workflow_id, _derive_dag_sha256, _build_capability_token,
_build_sandbox_envelope, _sha256_hex, _canonical_json), and the full
l3_orchestrate_apps_lic happy path + its TypeError / ValueError guards.
All real RouteContract / FinalEvidenceContract instances — no mocks. L3 is a
pure decision binding (no I/O, no L4 write), so the whole surface is unit
testable.
"""

from __future__ import annotations

import pytest

from agentic_core.runtime.contracts.final_evidence_contract import FinalEvidenceContract
from agentic_core.runtime.contracts.route_contract import RouteContract
from apps_lic.runtime.bindings import l3_binding as mod
from apps_lic.runtime.bindings.l3_binding import (
    APPS_LIC_DAG_ID,
    APPS_LIC_L3_CERT_REF,
    APPS_LIC_NODE_ID,
    APPS_LIC_WORKFLOW_TYPE,
    _build_capability_token,
    _build_sandbox_envelope,
    _canonical_json,
    _derive_dag_sha256,
    _derive_workflow_id,
    _sha256_hex,
    l3_orchestrate_apps_lic,
)


def _route(execution_form: str = "managed_workflow", **kw) -> RouteContract:
    base = dict(
        request_id="rq1",
        run_id="run1",
        app_id="apps_lic",
        trace_id="tr1",
        route_id="rt1",
        l3_required=True,
        grounding_required=False,
        model_generation_required=True,
        write_authority_present=False,
        execution_form=execution_form,
        l5_certification_ref="route-cert",
    )
    base.update(kw)
    return RouteContract(**base)


def _fec(**kw) -> FinalEvidenceContract:
    base = dict(
        request_id="rq1",
        run_id="run1",
        app_id="apps_lic",
        trace_id="tr1",
        l5_certification_ref="fec-cert",
    )
    base.update(kw)
    return FinalEvidenceContract(**base)


class TestTopologyConstants:
    def test_node_and_dag_ids(self) -> None:
        assert APPS_LIC_NODE_ID == "apps_lic.hop_pipeline.execute"
        assert APPS_LIC_DAG_ID == "apps_lic.hop_pipeline.dag_v1"
        assert APPS_LIC_WORKFLOW_TYPE == "outreach_message_managed"

    def test_cert_ref_nonempty(self) -> None:
        assert isinstance(APPS_LIC_L3_CERT_REF, str) and APPS_LIC_L3_CERT_REF


class TestPureHelpers:
    def test_sha256_hex_deterministic(self) -> None:
        assert _sha256_hex("x") == _sha256_hex("x")
        assert len(_sha256_hex("x")) == 64

    def test_canonical_json_sorted_keys(self) -> None:
        assert _canonical_json({"b": 1, "a": 2}) == '{"a":2,"b":1}'

    def test_derive_workflow_id_length_and_determinism(self) -> None:
        r = _route()
        wf1 = _derive_workflow_id(r)
        wf2 = _derive_workflow_id(r)
        assert wf1 == wf2
        assert len(wf1) == 24

    def test_derive_workflow_id_varies_by_route(self) -> None:
        a = _derive_workflow_id(_route(route_id="A"))
        b = _derive_workflow_id(_route(route_id="B"))
        assert a != b

    def test_derive_dag_sha256_prefixed(self) -> None:
        dag = _derive_dag_sha256("wf-123")
        assert dag.startswith("sha256:")
        assert _derive_dag_sha256("wf-123") == dag

    def test_capability_token_prefixed_and_deterministic(self) -> None:
        r = _route()
        tok = _build_capability_token(r)
        assert tok.startswith("cap:")
        assert _build_capability_token(r) == tok

    def test_sandbox_envelope_prefixed(self) -> None:
        env = _build_sandbox_envelope(_route())
        assert env.startswith("sbx:")


class TestOrchestrateGuards:
    def test_wrong_route_type_raises(self) -> None:
        with pytest.raises(TypeError, match="expected RouteContract"):
            l3_orchestrate_apps_lic("not-a-route", _fec())  # type: ignore[arg-type]

    def test_wrong_fec_type_raises(self) -> None:
        with pytest.raises(TypeError, match="expected FinalEvidenceContract"):
            l3_orchestrate_apps_lic(_route(), "not-a-fec")  # type: ignore[arg-type]

    def test_non_managed_workflow_raises(self) -> None:
        with pytest.raises(ValueError, match="managed_workflow"):
            l3_orchestrate_apps_lic(_route(execution_form="direct_answer"), _fec())


class TestOrchestrateHappyPath:
    def test_returns_three_artifacts(self) -> None:
        receipt, step, bus = l3_orchestrate_apps_lic(_route(), _fec())
        assert receipt is not None
        assert step is not None
        assert bus is not None

    def test_receipt_node_and_dag(self) -> None:
        receipt, _, _ = l3_orchestrate_apps_lic(_route(), _fec())
        assert receipt.selected_node_ids == (APPS_LIC_NODE_ID,)
        assert receipt.dag_id == APPS_LIC_DAG_ID
        assert receipt.l5_certification_ref == APPS_LIC_L3_CERT_REF

    def test_step_contract_bounds(self) -> None:
        _, step, _ = l3_orchestrate_apps_lic(_route(), _fec())
        assert step.node_id == APPS_LIC_NODE_ID
        assert step.parent_route_id == "rt1"
        assert step.timeout_ms == 180_000
        assert step.no_durable_commit_authority is True
        assert step.expected_output_contract == "SealedL2Artifact"

    def test_step_capability_and_sandbox_match_helpers(self) -> None:
        route = _route()
        _, step, _ = l3_orchestrate_apps_lic(route, _fec())
        assert step.capability_token_requirement == _build_capability_token(route)
        assert step.sandbox_envelope_requirement == _build_sandbox_envelope(route)

    def test_context_bus_workflow_id_matches_derivation(self) -> None:
        route = _route()
        _, _, bus = l3_orchestrate_apps_lic(route, _fec())
        assert bus.workflow_id == _derive_workflow_id(route)

    def test_deterministic_across_calls(self) -> None:
        r, f = _route(), _fec()
        _, step1, _ = l3_orchestrate_apps_lic(r, f)
        _, step2, _ = l3_orchestrate_apps_lic(r, f)
        assert step1.step_contract_id == step2.step_contract_id
        assert step1.step_contract_hash == step2.step_contract_hash

    def test_evidence_refs_carried_from_fec(self) -> None:
        # FEC with a compilation_hash should surface a fec: evidence ref on the bus.
        fec = _fec(compilation_hash="abc123def456")
        _, _, bus = l3_orchestrate_apps_lic(_route(), fec)
        assert any(ref.startswith("fec:") for ref in bus.carried_evidence_refs)

    def test_tenant_id_default_when_blank(self) -> None:
        receipt, _, _ = l3_orchestrate_apps_lic(_route(tenant_id=""), _fec())
        assert receipt.tenant_id == "apps_lic"
