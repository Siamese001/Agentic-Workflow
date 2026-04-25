"""Shared fixtures for v6 Exit Evaluation tests."""

from __future__ import annotations

from typing import Any

from agentic_core.L3_orchestration.exit_eval.v6 import (
    ExitReviewPacket,
    SourceType,
    normalize_to_packet,
)


def base_receipts(**overrides: Any) -> dict[str, Any]:
    """A receipt dict that passes 5.0 immediate-fail validation for answer-only."""
    base: dict[str, Any] = {
        "source_type": "L2_SEALED_ARTIFACT",
        "request_id": "req-1",
        "run_id": "run-1",
        "session_id": "sess-1",
        "trace_root": "trace-1",
        "route_id": "R3",
        "policy_hash": "pol::v1",
        "blueprint_hash": "bp::v1",
        "prompt_hash": "ph::v1",
        "replay_key": "rk-1",
        "compliance_hash": "comp-1",
        "manifest_hash": "mh-1",
        "hmac_sig": "sig-1",
        "route_contract": {
            "route_id": "R3",
            "policy_hash": "pol::v1",
            "blueprint_hash": "bp::v1",
            "prompt_hash": "ph::v1",
        },
        "sandbox_envelope": {"isolation_intact": True},
        "capability_token": {"authorizes_write": False, "expired": False},
        "provider_lane": "default",
        "cost_tier": "low",
        "slo_slice": {"latency_ms": 30000},
        "timeout_ms": 30000,
        "budget_counters": {"used_tokens": 100, "max_tokens": 4000},
        "terminal_class": "answer_only",
        "exec_trace": {
            "tool_calls": [],
            "model_calls": [{"model_id": "m1"}],
            "replay_receipts_present": True,
            "wall_clock_used": False,
        },
        "state_diff": {},
        "write_intent_class": "",
        "evidence_bundle": {},
        "final_evidence_contract": {},
        "prompt_assembly_status": {"slot_order_valid": True},
        "compiled_prompt_artifact": {},
        "output": {
            "text": "Paris is the capital of France.",
            "schema_required": False,
            "schema_valid": True,
            "groundedness": 0.95,
            "faithfulness": 0.95,
            "citation_precision": 0.95,
            "completion_score": 0.9,
            "confidence": 0.7,
            "format_fit": True,
        },
        "validation_counters": {},
        "retry_counters": {"retry_count": 0, "retry_max": 3},
        "repair_counters": {},
        "trajectory_snapshot": {},
        "grader_composition": {
            "roster": ["code_schema", "code_citation"],
            "threshold_profile": "production_v1",
        },
        "track_label": "production",
        "support_score": 0.9,
        "confidence": 0.7,
        "abstain_flags": [],
        "contradiction_flags": [],
        "otel_spans": {
            "spans": {
                "trace_root": "t1",
                "route_contract": "rc1",
                "tool_invocations": ["i1"],
                "evidence_contracts": ["e1"],
                "step_outputs": ["s1"],
                "exit_disposition": "ALLOW",
            },
        },
        "timing_offsets": {},
        "anomaly_flags": [],
        "hitl_packet": {},
        "bus_d_signals": [],
        "bus_e_signals": [],
        "replay_guard_violations": [],
        "isolation_anomalies": [],
        "drift_warnings": [],
    }
    base.update(overrides)
    return base


def base_packet(**overrides: Any) -> ExitReviewPacket:
    return normalize_to_packet(base_receipts(**overrides))


__all__ = ["base_receipts", "base_packet"]
