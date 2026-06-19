from __future__ import annotations

from agentic_core.L6_observability.shadow_eval import (
    L6_GATE_FAIL,
    L6_GATE_PASS,
    L6PipelineState,
    build_g29_learning_firewall_receipt,
    build_surface_isolation_manifest,
    record_denied_write_attempt,
    run_6a,
    run_observer,
)


def _raw_exhaust(*, l5_ref: str = "l5-cert-ref:g28") -> dict[str, object]:
    return {
        "runtime_boundary_crossed": True,
        "completed_at": "2026-06-13T00:00:00+00:00",
        "request_id": "req-g28",
        "run_id": "run-g28",
        "session_id": "sess-g28",
        "tenant_id": "tenant-g28",
        "trace_root": "trace-g28",
        "exit_disposition_ref": "exit-g28",
        "exit_disposition": "ALLOW_FINISH",
        "route_id": "route-g28",
        "execution_form": "test",
        "terminal_class": "normal_success",
        "outcome_class": "normal_success",
        "policy_hash": "policy-g28",
        "blueprint_hash": "blueprint-g28",
        "replay_key": "replay-g28",
        "route_contract_ref": "route-contract-g28",
        "source_lineage_manifest_ref": "lineage-g28",
        "l5_certification_ref": l5_ref,
        "source_exhaust": [
            {
                "source_type": "test",
                "source_ref": "exit-g28",
                "source_hash": "sha256:g28",
                "source_schema_version": "v40",
                "observed_stage": "EXIT",
                "expected_stage_order": 7,
                "lineage_parent_refs": ["trace-g28"],
                "completeness_status": "COMPLETE",
                "trust_status": "TRUSTED",
            }
        ],
        "events": [
            {
                "event_type": "test",
                "stage": "EXIT",
                "source_ref": "exit-g28",
                "payload_ref": "payload-g28",
                "trace_id": "trace-g28",
                "span_id": "span-g28",
                "parent_span_id": None,
                "provider_lane": "test",
                "prompt_hash": "prompt-g28",
                "context_hash": "ctx-g28",
                "artifact_digest": "artifact-g28",
                "eval_readiness_hint": "READY",
            }
        ],
        "artifacts": {
            "generated": ["artifact-g28"],
            "sealed": ["artifact-g28"],
            "file_hashes": {"artifact-g28": "sha256:g28"},
            "artifact_lineage": {"artifact-g28": ["trace-g28"]},
        },
    }


def test_g28_g29_pass_with_complete_v40_evidence() -> None:
    state = L6PipelineState()
    run_6a(state, _raw_exhaust())
    readiness = run_observer(state)

    assert state.g28 is not None
    assert state.g29 is not None
    assert state.g28.verdict == L6_GATE_PASS
    assert state.g29.verdict == L6_GATE_PASS
    assert readiness.l5_certification_status == "PRESENT"
    assert readiness.g28_audit_completeness_receipt_ref == state.g28.gate_receipt_id


def test_g28_fails_missing_l5_sentinel_and_readiness_holds() -> None:
    state = L6PipelineState()
    run_6a(state, _raw_exhaust(l5_ref=""))
    readiness = run_observer(state)

    assert state.g28 is not None
    assert state.g28.verdict == L6_GATE_FAIL
    assert "l5_certification_ref" in readiness.reason_codes
    assert readiness.l5_certification_status == "MISSING"


def test_g28_fails_generated_apps_eval_l5_ref_and_readiness_holds() -> None:
    state = L6PipelineState()
    run_6a(state, _raw_exhaust(l5_ref="l5-cert-ref:apps_eval:record-001"))
    readiness = run_observer(state)

    assert state.g28 is not None
    assert state.g28.verdict == L6_GATE_FAIL
    assert "l5_certification_ref" in state.g28.missing_refs
    assert "L5_CERT_REF_UNRESOLVED" in readiness.reason_codes
    assert readiness.l5_certification_status == "MISSING"


def test_g29_blocks_current_run_x3_mutation_attempt() -> None:
    state = L6PipelineState()
    ingest = run_6a(state, _raw_exhaust())
    denied = record_denied_write_attempt(
        ingest.bundle,
        surface="current_run_x3",
        operation="mutate",
        reason_code="CURRENT_RUN_X3_MUTATION_FORBIDDEN",
    )
    isolation = build_surface_isolation_manifest(
        ingest.bundle,
        read_surfaces_touched=("traces",),
        write_surfaces_requested=("current_run_x3",),
        denied_write_attempts=(denied,),
    )

    receipt = build_g29_learning_firewall_receipt(ingest.bundle, isolation=isolation)

    assert receipt.verdict == L6_GATE_FAIL
    assert "no_current_run_mutation_attempt" in receipt.forbidden_attempts
    assert "no_current_run_x3_mutation" in receipt.forbidden_attempts
