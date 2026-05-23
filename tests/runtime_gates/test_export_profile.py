"""00C parent export profile (optional auditor projection)."""

from __future__ import annotations

import pytest

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


class TestExportProfileEdgeCases:
    def test_parent_native_disposition_passthrough(self) -> None:
        assert export_disposition("REROUTE_HINT") == "REROUTE_HINT"
        assert export_disposition("ESCALATE_HINT") == "ESCALATE_HINT"

    def test_unknown_mesh_disposition_raises(self) -> None:
        with pytest.raises(ValueError, match="Cannot map mesh disposition"):
            export_disposition("TOTALLY_UNKNOWN_DISPOSITION")

    def test_empty_disposition_raises(self) -> None:
        with pytest.raises(ValueError, match="Cannot map mesh disposition"):
            export_disposition("")

    def test_export_result_unknown_mesh_maps_to_unknown(self) -> None:
        assert export_result("BOGUS_RESULT") == "UNKNOWN"

    def test_invalid_severity_defaults_to_info(self) -> None:
        out = gate_verdict_to_parent_export(
            {
                "gate_id": "G01",
                "result": "PASS",
                "disposition": "ALLOW",
                "severity": "NOT_A_REAL_SEVERITY",
            }
        )
        assert out["severity"] == "info"

    def test_export_verdict_bundle_preserves_order(self) -> None:
        from agentic_core.L5_safety.runtime_gates.export_profile import export_verdict_bundle

        verdicts = [
            {"gate_id": "G01", "result": "PASS", "disposition": "ALLOW"},
            {"gate_id": "G02", "result": "FAIL", "disposition": "DENY"},
        ]
        out = export_verdict_bundle(verdicts)
        assert [v["gate_id"] for v in out] == ["G01", "G02"]
        assert out[1]["disposition"] == "DENY"

    def test_abstain_maps_to_deny_in_parent_export(self) -> None:
        out = gate_verdict_to_parent_export(
            {
                "gate_id": "G10",
                "result": "FAIL",
                "disposition": "ABSTAIN",
            }
        )
        assert out["disposition"] == "DENY"
