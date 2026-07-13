"""Regression — runtime span records  →  L6 shadow ``raw_exhaust`` bridge (Phase 4).

Proves the adapter produces linked, stage-mapped events and that the real L6
ingest (``shadow_eval.ingest.build_runtime_exhaust_bundle``) consumes that output
to produce normalized evidence — with no live OTEL backend involved.
"""

from __future__ import annotations

from agentic_core.L6_observability.shadow_eval.ingest import (
    build_runtime_exhaust_bundle,
)
from agentic_core.runtime.exhaust.shadow_raw_exhaust_adapter import (
    build_l6_shadow_raw_exhaust,
    build_l6_shadow_raw_exhaust_from_runtime_bundle,
)
from agentic_core.runtime.exhaust.runtime_exhaust_bundle import (
    build_runtime_exhaust_bundle as build_post_exit_bundle,
)

_REQUIRED_EVENT_KEYS = {
    "trace_id",
    "span_id",
    "parent_span_id",
    "stage",
    "event_type",
    "source_ref",
    "payload_ref",
}


def _sample_spans():
    return [
        {
            "ts_utc": 1710000000000,
            "duration_ms": 1.0,
            "kind": "trace_root",
            "trace_id": "trace-abc",
            "span_id": "span-root",
            "parent_span_id": "",
            "layer": "L0_routing",
            "component": "RuntimeIntake",
            "name": "runtime.trace_root",
            "status": "ok",
            "attributes": {"run_id": "run-1", "request_id": "req-1"},
        },
        {
            "ts_utc": 1710000000100,
            "duration_ms": 5.0,
            "kind": "seal",
            "trace_id": "trace-abc",
            "span_id": "span-l2",
            "parent_span_id": "span-root",
            "layer": "L2_execution",
            "component": "L2Execution",
            "name": "L2.step.seal",
            "status": "ok",
            "attributes": {"step_id": "step-1", "replay_key": "replay-1"},
        },
        {
            "ts_utc": 1710000000200,
            "duration_ms": 1.0,
            "kind": "exit",
            "trace_id": "trace-abc",
            "span_id": "span-exit",
            "parent_span_id": "span-l2",
            "layer": "L5_safety",
            "component": "ExitGate",
            "name": "exit.disposition",
            "status": "ok",
            "attributes": {"exit_disposition": "allow", "policy_hash": "policy-1"},
        },
    ]


def _full_raw_exhaust(spans):
    return build_l6_shadow_raw_exhaust(
        request_id="req-1",
        run_id="run-1",
        trace_root="trace-abc",
        completed_at="2026-06-14T00:00:00Z",
        runtime_boundary_crossed=True,
        exit_disposition_ref="exit-disp-digest-1",
        spans=spans,
        policy_hash="policy-1",
        replay_key="replay-1",
        route_contract_ref="route-contract-1",
    )


def test_adapter_builds_raw_exhaust_with_linked_events():
    raw = _full_raw_exhaust(_sample_spans())

    assert raw["trace_root"] == "trace-abc"
    assert raw["runtime_boundary_crossed"] is True
    assert raw["exit_disposition_ref"]
    assert len(raw["events"]) == 3

    for ev in raw["events"]:
        assert _REQUIRED_EVENT_KEYS.issubset(ev.keys())
        assert ev["source_ref"].startswith("span:")
        assert ev["payload_ref"].startswith("span-payload:")

    assert [ev["stage"] for ev in raw["events"]] == ["L0", "L2", "EXIT"]
    # span linkage is preserved end-to-end
    assert raw["events"][1]["parent_span_id"] == "span-root"
    assert raw["events"][2]["parent_span_id"] == "span-l2"


def test_adapter_derives_trace_root_and_completed_at_when_omitted():
    raw = build_l6_shadow_raw_exhaust(
        request_id="req-1",
        run_id="run-1",
        runtime_boundary_crossed=True,
        exit_disposition_ref="exit-disp-digest-1",
        spans=_sample_spans(),
    )
    assert raw["trace_root"] == "trace-abc"  # derived from first span trace_id
    assert raw["completed_at"]  # auto-filled (L6 ingest requires it non-empty)


def test_l6_ingest_consumes_adapter_output_without_live_otel():
    raw = _full_raw_exhaust(_sample_spans())
    bundle, normalized, manifests, stage_map, _inv, _gap = build_runtime_exhaust_bundle(raw)

    assert bundle.trace_root == "trace-abc"
    assert len(normalized) == 3
    assert len(manifests) == 3
    assert {"L0", "L2", "EXIT"}.issubset(set(stage_map.observed_stages))
    assert all(r.trace_id == "trace-abc" for r in normalized)
    # the source manifests are marked as sealed runtime exhaust, runtime-span-v1
    assert all(m.trust_status == "SEALED_RUNTIME_EXHAUST" for m in manifests)


def test_post_exit_bundle_adapter_binds_existing_sealed_evidence():
    bundle = build_post_exit_bundle(
        request_id="req-1",
        run_id="run-1",
        trace_root="trace-abc",
        route_contract_ref="route-contract-1",
        sealed_result_ref="sealed-result-1",
        gate_mesh_result_ref="gate-mesh-1",
        exit_disposition_ref="exit-disp-digest-1",
        runtime_receipt_refs=("runtime-receipt-1",),
        l5_certification_packet_ref="l5-cert-ref:test",
    )
    raw = build_l6_shadow_raw_exhaust_from_runtime_bundle(
        bundle,
        spans=_sample_spans(),
        policy_hash="policy-1",
        blueprint_hash="blueprint-1",
    )
    assert raw["policy_hash"] == "policy-1"
    assert raw["blueprint_hash"] == "blueprint-1"
    assert raw["source_lineage_manifest_ref"] == f"runtime-exhaust:{bundle.bundle_id}"
    assert set(raw["artifacts"]["sealed"]) == {
        "sealed-result-1",
        "gate-mesh-1",
        "exit-disp-digest-1",
        "runtime-receipt-1",
    }
