"""L0/L3 span digest replay (plan l0-l3 W4)."""
from __future__ import annotations

from dataclasses import replace

from agentic_core.runtime.contracts.final_evidence_contract import FinalEvidenceContract
from agentic_core.runtime.contracts.route_contract import RouteContract

from apps_rg.runtime.bindings.l0_l3_otel_spans import (
    emit_l0_route_span,
    emit_l3_orchestration_span,
)
from apps_rg.runtime.bindings.l3_binding import l3_orchestrate_apps_rg


def _route() -> RouteContract:
    return RouteContract(
        request_id="req-replay",
        run_id="run-replay",
        app_id="apps_rg",
        trace_id="trace-replay",
        route_id="R4_MANAGED_DRAFT",
        execution_form="managed_workflow",
        l3_required=True,
        grounding_required=True,
        model_generation_required=True,
        write_authority_present=False,
        route_digest="deadbeef" * 8,
        l5_certification_ref="test:valid:w6",
    )


def test_l0_l3_span_digests_byte_identical() -> None:
    r = _route()
    s0 = emit_l0_route_span(r)
    assert s0 is not None
    d0a = s0["payload_digest"]
    d0b = emit_l0_route_span(r)["payload_digest"]
    assert d0a == d0b

    fec = FinalEvidenceContract(
        request_id=r.request_id,
        run_id=r.run_id,
        app_id=r.app_id,
        trace_id=r.trace_id,
        compilation_hash="fec",
        evidence_items=(),
        l5_certification_ref="test:valid:w6",
    )
    receipt, _, _ = l3_orchestrate_apps_rg(r, fec)
    wf = receipt.dag_id
    s1 = emit_l3_orchestration_span(route=r, workflow_id="wf1", dag_id=wf)
    s2 = emit_l3_orchestration_span(route=r, workflow_id="wf1", dag_id=wf)
    assert s1 and s2
    assert s1["payload_digest"] == s2["payload_digest"]
