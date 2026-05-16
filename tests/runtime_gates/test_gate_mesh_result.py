"""00C.7 GateMeshResult schema and aggregation tests.

Proof command:
    python -m pytest tests/runtime_gates/test_gate_mesh_result.py -q
"""

from __future__ import annotations

from agentic_core.L5_safety.runtime_gates.mesh_result import (
    GateMeshResult,
    build_mesh_result,
)
from agentic_core.L5_safety.runtime_gates.contracts import (
    Disposition,
    GateDecision,
    Result,
    Severity,
)


def _ok(gid: str = "G01") -> GateDecision:
    return GateDecision(gate_id=gid, disposition=Disposition.ALLOW)


def test_required_fields_present():
    bundle = build_mesh_result(
        [_ok()], required_gate_ids=["G01"], evaluated_surface="U0"
    )
    payload = bundle.to_dict()
    for key in (
        "request_id",
        "run_id",
        "trace_root",
        "evaluated_surface",
        "evaluated_packet_ref",
        "required_gate_ids",
        "completed_gate_ids",
        "missing_gate_ids",
        "verdicts",
        "hard_fail_present",
        "unknown_material_present",
        "warn_material_present",
        "recommended_next_owner",
        "deterministic_digest",
        "gate_mesh_schema_version",
    ):
        assert key in payload


def test_completed_and_missing_disjoint():
    bundle = build_mesh_result(
        [_ok("G01"), _ok("G02")],
        required_gate_ids=["G01", "G02", "G03"],
        evaluated_surface="U0",
    )
    assert set(bundle.completed_gate_ids).isdisjoint(set(bundle.missing_gate_ids))
    assert bundle.missing_gate_ids == ["G03"]


def test_pass_only_aggregates_to_allow():
    bundle = build_mesh_result(
        [_ok("G01"), _ok("G02")],
        required_gate_ids=["G01", "G02"],
        evaluated_surface="U0",
    )
    assert bundle.recommended_disposition_summary == "ALLOW"
    assert bundle.hard_fail_present is False


def test_critical_warn_aggregates_to_mark_degraded():
    decisions = [
        _ok("G01"),
        GateDecision(
            gate_id="G22",
            disposition=Disposition.MARK_DEGRADED,
            result=Result.WARN,
            severity=Severity.HIGH,
        ),
    ]
    bundle = build_mesh_result(
        decisions, required_gate_ids=["G01", "G22"], evaluated_surface="EXIT"
    )
    assert bundle.warn_material_present is True
    assert bundle.recommended_disposition_summary == "MARK_DEGRADED"


def test_digest_changes_when_verdict_changes():
    a = build_mesh_result([_ok("G01")], required_gate_ids=["G01"], evaluated_surface="U0")
    b = build_mesh_result(
        [GateDecision(gate_id="G01", disposition=Disposition.DENY, reason_codes=["x"])],
        required_gate_ids=["G01"],
        evaluated_surface="U0",
    )
    assert a.deterministic_digest != b.deterministic_digest


def test_immutable_verdict_lists_per_doctrine():
    decisions = [_ok("G01")]
    bundle = build_mesh_result(
        decisions, required_gate_ids=["G01"], evaluated_surface="U0"
    )
    # Mutating returned dict-from-to_dict must not affect the source bundle.
    payload = bundle.to_dict()
    payload["verdicts"].append({"gate_id": "G99"})
    assert len(bundle.verdicts) == 1


def test_mesh_result_is_dataclass_instance():
    bundle = build_mesh_result(
        [_ok("G01")], required_gate_ids=["G01"], evaluated_surface="U0"
    )
    assert isinstance(bundle, GateMeshResult)
