"""apps_rg L3 binding smoke tests."""
from __future__ import annotations

from dataclasses import replace

from agentic_core.runtime.contracts.final_evidence_contract import FinalEvidenceContract
from agentic_core.runtime.contracts.route_contract import RouteContract

from apps_rg.runtime.bindings.l3_binding import l3_orchestrate_apps_rg


def _route() -> RouteContract:
    return RouteContract(
        request_id="req-1",
        run_id="run-1",
        app_id="apps_rg",
        trace_id="trace-1",
        route_id="R4_MANAGED_DRAFT",
        execution_form="managed_workflow",
        l3_required=True,
        grounding_required=True,
        model_generation_required=True,
        write_authority_present=False,
        route_digest="abc123",
        l5_certification_ref="test:valid:w6",
    )


def test_l3_orchestrate_apps_rg_receipt() -> None:
    fec = FinalEvidenceContract(
        request_id="req-1",
        run_id="run-1",
        app_id="apps_rg",
        trace_id="trace-1",
        compilation_hash="fec-hash",
        evidence_items=(),
        l5_certification_ref="test:valid:w6",
    )
    receipt, step, bus = l3_orchestrate_apps_rg(_route(), fec)
    assert receipt.l3_no_execute_assertion is True
    assert step.node_id == "apps_rg.modular_resume.execute"
    assert bus.workflow_id


def test_l3_rejects_non_managed() -> None:
    fec = FinalEvidenceContract(
        request_id="req-1",
        run_id="run-1",
        app_id="apps_rg",
        trace_id="trace-1",
        compilation_hash="x",
        evidence_items=(),
        l5_certification_ref="test:valid:w6",
    )
    bad = replace(_route(), execution_form="direct")
    try:
        l3_orchestrate_apps_rg(bad, fec)
        raised = False
    except ValueError:
        raised = True
    assert raised
