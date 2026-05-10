"""Shared fixtures for L6 shadow_eval test pack (06.x)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


@pytest.fixture
def sealed_completed_run() -> dict:
    """A minimally complete sealed exhaust packet that satisfies 6A.

    Includes Exit disposition, trace_root, replay_key, policy_hash, blueprint_hash,
    and at least one normalized event with a span/trace pair.
    """
    return {
        "runtime_boundary_crossed": True,
        "completed_at": _ts(),
        "request_id": "req-001",
        "run_id": "run-001",
        "session_id": "sess-001",
        "tenant_id": "tenant-A",
        "trace_root": "trace-root-001",
        "exit_disposition_ref": "exit-001",
        "exit_disposition": "ALLOW_FINISH",
        "route_id": "route-001",
        "execution_form": "RET",
        "terminal_class": "normal_success",
        "outcome_class": "normal_success",
        "policy_hash": "policy-hash-A",
        "blueprint_hash": "blueprint-hash-A",
        "replay_key": "replay-key-A",
        "route_contract_ref": "route-contract-001",
        "l1_plan_ref": "plan-001",
        "c0_evidence_contract_refs": ["ec-001"],
        "prompt_envelope_refs": ["env-001"],
        "l2_artifact_refs": ["l2-art-001"],
        "uwg_receipt_refs": ["uwg-001"],
        "uwg_commit_status": "COMMITTED",
        "l5_certification_ref": "l5-cert-ref:test-run-001",
        "source_lineage_manifest_ref": "lineage-001",
        "source_exhaust": [
            {
                "source_type": "otel_span",
                "source_ref": "span-1",
                "source_hash": "h1",
                "observed_stage": "L0",
                "expected_stage_order": 1,
                "lineage_parent_refs": ["root"],
                "completeness_status": "COMPLETE",
                "trust_status": "TRUSTED",
            },
            {
                "source_type": "otel_span",
                "source_ref": "span-2",
                "source_hash": "h2",
                "observed_stage": "L2",
                "expected_stage_order": 2,
                "lineage_parent_refs": ["span-1"],
                "completeness_status": "COMPLETE",
                "trust_status": "TRUSTED",
            },
            {
                "source_type": "exit_disposition",
                "source_ref": "exit-001",
                "source_hash": "h3",
                "observed_stage": "EXIT",
                "expected_stage_order": 3,
                "lineage_parent_refs": ["span-2"],
                "completeness_status": "COMPLETE",
                "trust_status": "TRUSTED",
            },
            {
                "source_type": "u0_envelope",
                "source_ref": "u0-1",
                "source_hash": "h4",
                "observed_stage": "U0",
                "expected_stage_order": 0,
                "lineage_parent_refs": [],
                "completeness_status": "COMPLETE",
                "trust_status": "TRUSTED",
            },
            {
                "source_type": "l1_plan",
                "source_ref": "plan-1",
                "source_hash": "h5",
                "observed_stage": "L1",
                "expected_stage_order": 1,
                "lineage_parent_refs": ["u0-1"],
                "completeness_status": "COMPLETE",
                "trust_status": "TRUSTED",
            },
        ],
        "events": [
            {
                "event_type": "tool_call",
                "stage": "L2",
                "source_ref": "span-2",
                "payload_ref": "payload-1",
                "trace_id": "trace-root-001",
                "span_id": "span-2",
                "parent_span_id": "span-1",
                "step_id": "step-1",
                "attempt_id": "attempt-1",
                "model_id": "claude-3.5-sonnet",
                "tool_id": "search",
                "provider_lane": "anthropic",
                "token_count_in": 100,
                "token_count_out": 50,
                "cost_estimate": 0.001,
                "latency_ms": 250.0,
                "retry_count": 0,
                "repair_count": 0,
                "fallback_depth": 0,
                "prompt_hash": "prompt-A",
                "context_hash": "ctx-A",
                "artifact_digest": "art-A",
                "eval_readiness_hint": "READY",
            }
        ],
        "artifacts": {
            "generated": ["art-001"],
            "sealed": ["art-001"],
            "file_hashes": {"art-001": "sha256:abc"},
            "artifact_lineage": {"art-001": ["span-2"]},
        },
    }


@pytest.fixture
def in_flight_run(sealed_completed_run) -> dict:
    """An in-flight run; runtime_boundary_crossed=False — must be rejected by 6A."""
    inflight = dict(sealed_completed_run)
    inflight["runtime_boundary_crossed"] = False
    return inflight


@pytest.fixture
def run_missing_exit(sealed_completed_run) -> dict:
    """Sealed run with Exit disposition removed."""
    no_exit = dict(sealed_completed_run)
    no_exit.pop("exit_disposition_ref", None)
    return no_exit


@pytest.fixture
def run_missing_replay_key(sealed_completed_run) -> dict:
    no_replay = dict(sealed_completed_run)
    no_replay.pop("replay_key", None)
    return no_replay


@pytest.fixture
def run_missing_trace_root(sealed_completed_run) -> dict:
    no_trace = dict(sealed_completed_run)
    no_trace["trace_root"] = ""
    return no_trace


@pytest.fixture
def run_missing_cert_ref(sealed_completed_run) -> dict:
    no_cert = dict(sealed_completed_run)
    no_cert.pop("l5_certification_ref", None)
    return no_cert


@pytest.fixture
def run_with_cert_ref(sealed_completed_run) -> dict:
    with_cert = dict(sealed_completed_run)
    with_cert["l5_certification_ref"] = "l5-cert-ref:run-certified-001"
    return with_cert
