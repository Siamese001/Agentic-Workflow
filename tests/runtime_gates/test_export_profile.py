"""00C parent export profile (optional auditor projection)."""

from __future__ import annotations

from agentic_core.L5_safety.runtime_gates.export_profile import (
    export_disposition,
    export_result,
    gate_verdict_to_parent_export,
)


def test_export_disposition_maps_mesh_to_parent() -> None:
    assert export_disposition("REROUTE") == "REROUTE_HINT"
    assert export_disposition("ESCALATE_HITL") == "ESCALATE_HINT"
    assert export_disposition("BLOCK_COMMIT") == "BLOCK_COMMIT"


def test_export_result_warn_maps_to_pass() -> None:
    assert export_result("WARN") == "PASS"


def test_gate_verdict_to_parent_export_shape() -> None:
    out = gate_verdict_to_parent_export(
        {
            "gate_id": "G07",
            "result": "PASS",
            "disposition": "ALLOW",
            "severity": "INFO",
            "reason_codes": ["ok"],
            "score": 1.0,
            "threshold": 0.5,
            "evidence_refs": [],
            "replay_refs": [],
            "confidence": 1.0,
            "abstain_flag": False,
            "remediation_hint": None,
            "policy_hash": "pol",
            "blueprint_hash": "blue",
            "replay_key": "rk",
            "schema_version": "00C-1.0.0",
        }
    )
    assert out["export_profile"] == "00C_parent_reqid_v1"
    assert out["disposition"] == "ALLOW"
    assert out["severity"] == "info"
