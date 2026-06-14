"""Unit tests for agentic_core.L5_safety.runtime_gates.mesh_result.

Wave 6.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — P2 L5 safety surface.
``mesh_result`` builds the doctrine 00C.7 ``GateMeshResult`` Exit consumes from a
list of ``GateDecision`` plus required gate IDs. Covers GateMeshResult defaults,
``to_dict`` round-trip, and the ``build_mesh_result`` aggregation rules:
hard-fail dominance, material UNKNOWN/WARN flags, missing-gate detection, and the
recommended-disposition precedence ladder.
"""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.runtime_gates.contracts import (
    SCHEMA_VERSION,
    Disposition,
    GateDecision,
    Result,
    Severity,
)
from agentic_core.L5_safety.runtime_gates.mesh_result import (
    GateMeshResult,
    build_mesh_result,
)


def _decision(
    gate_id: str,
    *,
    disposition: Disposition = Disposition.ALLOW,
    result: Result = Result.PASS,
    severity: Severity = Severity.INFO,
) -> GateDecision:
    return GateDecision(
        gate_id=gate_id,
        disposition=disposition,
        result=result,
        severity=severity,
    )


class TestGateMeshResultDefaults:
    def test_required_fields_and_defaults(self) -> None:
        r = GateMeshResult(
            request_id="req-1",
            run_id="run-1",
            trace_root="trace-1",
            evaluated_surface="answer",
            evaluated_packet_ref="pkt-1",
        )
        assert r.required_gate_ids == []
        assert r.completed_gate_ids == []
        assert r.missing_gate_ids == []
        assert r.verdicts == []
        assert r.hard_fail_present is False
        assert r.unknown_material_present is False
        assert r.warn_material_present is False
        assert r.recommended_next_owner == "EXIT"
        assert r.recommended_disposition_summary == ""
        assert r.deterministic_digest == ""
        assert r.route_id == ""
        assert r.gate_mesh_schema_version == SCHEMA_VERSION

    def test_default_list_fields_are_independent(self) -> None:
        a = GateMeshResult("r", "ru", "t", "s", "p")
        b = GateMeshResult("r", "ru", "t", "s", "p")
        a.required_gate_ids.append("G01")
        assert b.required_gate_ids == []

    def test_to_dict_keys_and_route_id(self) -> None:
        r = GateMeshResult("req", "run", "tr", "surf", "pkt", route_id="R4")
        d = r.to_dict()
        assert d["request_id"] == "req"
        assert d["route_id"] == "R4"
        assert d["evaluated_surface"] == "surf"
        assert d["gate_mesh_schema_version"] == SCHEMA_VERSION
        # to_dict copies the list fields, not aliases them.
        d["required_gate_ids"].append("X")
        assert r.required_gate_ids == []


class TestBuildMeshResultAllow:
    def test_all_pass_allows(self) -> None:
        decisions = [_decision("G01"), _decision("G02")]
        r = build_mesh_result(
            decisions,
            required_gate_ids=["G01", "G02"],
            evaluated_surface="answer",
        )
        assert r.recommended_disposition_summary == "ALLOW"
        assert r.hard_fail_present is False
        assert r.completed_gate_ids == ["G01", "G02"]
        assert r.missing_gate_ids == []

    def test_digest_is_populated_and_deterministic(self) -> None:
        decisions = [_decision("G01")]
        r1 = build_mesh_result(decisions, required_gate_ids=["G01"], evaluated_surface="s")
        r2 = build_mesh_result(
            [_decision("G01")], required_gate_ids=["G01"], evaluated_surface="s"
        )
        assert r1.deterministic_digest
        assert r1.deterministic_digest == r2.deterministic_digest

    def test_verdicts_get_per_verdict_digest(self) -> None:
        r = build_mesh_result(
            [_decision("G01")], required_gate_ids=["G01"], evaluated_surface="s"
        )
        assert r.verdicts[0]["deterministic_digest"]

    def test_passthrough_identity_fields(self) -> None:
        r = build_mesh_result(
            [_decision("G01")],
            required_gate_ids=["G01"],
            evaluated_surface="answer",
            evaluated_packet_ref="pkt",
            request_id="req",
            run_id="run",
            trace_root="tr",
            route_id="R4",
            recommended_next_owner="UWG",
        )
        assert r.request_id == "req"
        assert r.run_id == "run"
        assert r.trace_root == "tr"
        assert r.route_id == "R4"
        assert r.recommended_next_owner == "UWG"


class TestBuildMeshResultDispositionLadder:
    def test_hard_fail_disposition_denies(self) -> None:
        decisions = [_decision("G01", disposition=Disposition.DENY)]
        r = build_mesh_result(decisions, required_gate_ids=["G01"], evaluated_surface="s")
        assert r.hard_fail_present is True
        assert r.recommended_disposition_summary == "DENY"

    @pytest.mark.parametrize(
        "disp", [Disposition.DENY, Disposition.BLOCK_COMMIT, Disposition.QUARANTINE]
    )
    def test_each_hard_fail_disposition(self, disp: Disposition) -> None:
        r = build_mesh_result(
            [_decision("G01", disposition=disp)],
            required_gate_ids=["G01"],
            evaluated_surface="s",
        )
        assert r.hard_fail_present is True

    def test_material_fail_result_is_hard_fail(self) -> None:
        # FAIL result with HIGH severity → hard fail even if disposition isn't a hard one.
        decisions = [
            _decision(
                "G01",
                disposition=Disposition.ABSTAIN,
                result=Result.FAIL,
                severity=Severity.HIGH,
            )
        ]
        r = build_mesh_result(decisions, required_gate_ids=["G01"], evaluated_surface="s")
        assert r.hard_fail_present is True
        assert r.recommended_disposition_summary == "DENY"

    def test_low_severity_fail_is_not_hard_fail(self) -> None:
        decisions = [
            _decision(
                "G01",
                disposition=Disposition.ABSTAIN,
                result=Result.FAIL,
                severity=Severity.LOW,
            )
        ]
        r = build_mesh_result(decisions, required_gate_ids=["G01"], evaluated_surface="s")
        assert r.hard_fail_present is False

    def test_material_unknown_escalates(self) -> None:
        decisions = [
            _decision(
                "G01",
                disposition=Disposition.ABSTAIN,
                result=Result.UNKNOWN,
                severity=Severity.CRITICAL,
            )
        ]
        r = build_mesh_result(decisions, required_gate_ids=["G01"], evaluated_surface="s")
        assert r.unknown_material_present is True
        assert r.recommended_disposition_summary == "ESCALATE_HITL"

    def test_missing_gate_blocks_exit(self) -> None:
        decisions = [_decision("G01")]
        r = build_mesh_result(
            decisions, required_gate_ids=["G01", "G02"], evaluated_surface="s"
        )
        assert r.missing_gate_ids == ["G02"]
        assert r.recommended_disposition_summary == "BLOCK_EXIT"

    def test_material_warn_marks_degraded(self) -> None:
        decisions = [
            _decision(
                "G01",
                disposition=Disposition.ALLOW,
                result=Result.WARN,
                severity=Severity.HIGH,
            )
        ]
        r = build_mesh_result(decisions, required_gate_ids=["G01"], evaluated_surface="s")
        assert r.warn_material_present is True
        assert r.recommended_disposition_summary == "MARK_DEGRADED"

    def test_hard_fail_dominates_warn_and_unknown(self) -> None:
        decisions = [
            _decision("G01", disposition=Disposition.DENY),
            _decision(
                "G02",
                disposition=Disposition.ALLOW,
                result=Result.WARN,
                severity=Severity.HIGH,
            ),
        ]
        r = build_mesh_result(
            decisions, required_gate_ids=["G01", "G02"], evaluated_surface="s"
        )
        assert r.recommended_disposition_summary == "DENY"

    def test_empty_decisions_allows_when_no_required(self) -> None:
        r = build_mesh_result([], required_gate_ids=[], evaluated_surface="s")
        assert r.recommended_disposition_summary == "ALLOW"
        assert r.completed_gate_ids == []
