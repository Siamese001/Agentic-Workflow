"""W8 tests — GateVerdict, GateMeshResult, gate profile resolver.

plan: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2 W8
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from agentic_core.runtime.gates.gate_types import (
    VERDICT_FAIL,
    VERDICT_NOT_APPLICABLE,
    VERDICT_PASS,
    VERDICT_UNKNOWN,
    VERDICT_WARN,
    GateMeshResult,
    GateVerdict,
    build_gate_mesh_result,
)
from agentic_core.runtime.gates.gate_profile_resolver import (
    GateProfile,
    GateProfileError,
    GateProfileResolver,
)
from agentic_core.runtime.contracts.sealed_workflow_types import (
    SealedSectionArtifact,
    SealedWorkflowPackage,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]

# ── Helpers ───────────────────────────────────────────────────────────────────

def _verdict(
    gate_id: str = "G21",
    result: str = VERDICT_PASS,
    severity: str = "hard_fail",
    not_applicable_reason: str = "",
    unknown_reason: str = "",
    reason_codes: tuple[str, ...] = (),
) -> GateVerdict:
    return GateVerdict(
        gate_id=gate_id,
        result=result,
        severity=severity,
        not_applicable_reason=not_applicable_reason,
        unknown_reason=unknown_reason,
        reason_codes=reason_codes,
        request_id="req-test",
        run_id="run-test",
        deterministic_digest=f"digest::{gate_id}::{result}",
        created_at="2026-05-11T00:00:00Z",
    )


def _pkg(
    node_ids: list[str] | None = None,
    merged: str = "merged content",
) -> SealedWorkflowPackage:
    sections = tuple(
        SealedSectionArtifact(
            node_id=nid,
            run_id="run-test",
            sealed_content=f"content::{nid}",
            terminal_class="success",
        )
        for nid in (node_ids or ["header_block", "professional_summary", "experience_block",
                                  "skills_block", "education_block"])
    )
    return SealedWorkflowPackage(
        package_id="pkg::test::001",
        run_id="run-test",
        trace_root="trace::test",
        route_contract_ref="rc::test",
        workflow_ref="wfm::apps_rg::resume_generation::v1",
        sealed_sections=sections,
        merged_content=merged,
        terminal_class="success",
    )


# ── GateVerdict invariants ────────────────────────────────────────────────────

class TestGateVerdictInvariants:
    def test_gate_verdict_unknown_is_never_pass(self):
        v = _verdict("G21", VERDICT_UNKNOWN)
        assert not v.is_pass
        assert v.is_material_unknown

    def test_gate_verdict_pass_is_only_pass(self):
        v = _verdict("G21", VERDICT_PASS)
        assert v.is_pass
        assert not v.is_material_unknown

    def test_gate_verdict_fail_is_not_pass(self):
        v = _verdict("G21", VERDICT_FAIL)
        assert not v.is_pass

    def test_gate_verdict_warn_is_not_pass(self):
        v = _verdict("G21", VERDICT_WARN, severity="warn")
        assert not v.is_pass

    def test_gate_verdict_not_applicable_is_not_pass(self):
        v = _verdict("G27", VERDICT_NOT_APPLICABLE,
                     not_applicable_reason="no writes")
        assert not v.is_pass
        assert v.is_not_applicable

    def test_gate_verdict_not_applicable_requires_reason(self):
        with pytest.raises(ValueError, match="NOT_APPLICABLE requires not_applicable_reason"):
            GateVerdict(
                gate_id="G27",
                result=VERDICT_NOT_APPLICABLE,
                not_applicable_reason="",  # missing
                deterministic_digest="d",
                created_at="2026-01-01T00:00:00Z",
            )

    def test_gate_verdict_not_applicable_with_reason_ok(self):
        v = GateVerdict(
            gate_id="G27",
            result=VERDICT_NOT_APPLICABLE,
            not_applicable_reason="no durable writes",
            deterministic_digest="d",
            created_at="2026-01-01T00:00:00Z",
        )
        assert v.is_not_applicable

    def test_gate_verdict_invalid_result_raises(self):
        with pytest.raises(ValueError, match="invalid result"):
            GateVerdict(
                gate_id="G21",
                result="MAYBE",
                deterministic_digest="d",
                created_at="2026-01-01T00:00:00Z",
            )

    def test_gate_verdict_as_dict_has_required_keys(self):
        v = _verdict("G21", VERDICT_PASS, reason_codes=("ok",))
        d = v.as_dict()
        for key in ("gate_id", "result", "severity", "reason_codes",
                    "evidence_refs", "deterministic_digest", "created_at",
                    "not_applicable_reason", "unknown_reason"):
            assert key in d

    def test_gate_verdict_hard_fail_flag(self):
        v = _verdict("G21", VERDICT_FAIL, severity="hard_fail")
        assert v.is_hard_fail

    def test_gate_verdict_non_hard_fail_warn(self):
        v = _verdict("G21", VERDICT_WARN, severity="warn")
        assert not v.is_hard_fail


# ── GateMeshResult invariants ─────────────────────────────────────────────────

class TestGateMeshResultInvariants:
    def test_gate_mesh_missing_required_gate_becomes_unknown(self):
        # required: G21 G22, but only G21 provided
        verdicts = (_verdict("G21", VERDICT_PASS),)
        mesh = build_gate_mesh_result(
            request_id="req", run_id="run", trace_root="trace",
            route_id="R5", evaluated_surface="managed_workflow",
            evaluated_packet_ref="pkg::001",
            required_gate_ids=("G21", "G22"),
            verdicts=verdicts,
        )
        assert "G22" in mesh.missing_gate_ids
        assert mesh.unknown_material_present  # missing → material unknown
        assert mesh.blocks_allow_finish

    def test_gate_mesh_hard_fail_blocks_allow_finish(self):
        verdicts = (
            _verdict("G21", VERDICT_PASS),
            _verdict("G22", VERDICT_FAIL, severity="hard_fail"),
        )
        mesh = build_gate_mesh_result(
            request_id="req", run_id="run", trace_root="trace",
            route_id="R5", evaluated_surface="managed_workflow",
            evaluated_packet_ref="pkg::001",
            required_gate_ids=("G21", "G22"),
            verdicts=verdicts,
        )
        assert mesh.hard_fail_present
        assert mesh.blocks_allow_finish

    def test_gate_mesh_material_unknown_blocks_allow_finish(self):
        verdicts = (
            _verdict("G21", VERDICT_PASS),
            _verdict("G22", VERDICT_UNKNOWN),
        )
        mesh = build_gate_mesh_result(
            request_id="req", run_id="run", trace_root="trace",
            route_id="R5", evaluated_surface="managed_workflow",
            evaluated_packet_ref="pkg::001",
            required_gate_ids=("G21", "G22"),
            verdicts=verdicts,
        )
        assert mesh.unknown_material_present
        assert mesh.blocks_allow_finish

    def test_gate_mesh_all_pass_does_not_block(self):
        verdicts = tuple(
            _verdict(gid, VERDICT_PASS)
            for gid in ("G21", "G22", "G23", "G24", "G26", "G28")
        )
        mesh = build_gate_mesh_result(
            request_id="req", run_id="run", trace_root="trace",
            route_id="R5", evaluated_surface="managed_workflow",
            evaluated_packet_ref="pkg::001",
            required_gate_ids=("G21", "G22", "G23", "G24", "G26", "G28"),
            verdicts=verdicts,
        )
        assert not mesh.blocks_allow_finish
        assert mesh.all_required_passed

    def test_gate_mesh_multiple_pass_dont_cancel_hard_fail(self):
        verdicts = (
            _verdict("G21", VERDICT_PASS),
            _verdict("G22", VERDICT_PASS),
            _verdict("G23", VERDICT_PASS),
            _verdict("G26", VERDICT_FAIL, severity="hard_fail"),  # one fail
        )
        mesh = build_gate_mesh_result(
            request_id="req", run_id="run", trace_root="trace",
            route_id="R5", evaluated_surface="managed_workflow",
            evaluated_packet_ref="pkg::001",
            required_gate_ids=("G21", "G22", "G23", "G26"),
            verdicts=verdicts,
        )
        assert mesh.hard_fail_present
        assert mesh.blocks_allow_finish

    def test_gate_mesh_get_verdict(self):
        verdicts = (_verdict("G21", VERDICT_PASS),)
        mesh = build_gate_mesh_result(
            request_id="req", run_id="run", trace_root="trace",
            route_id="R5", evaluated_surface="managed_workflow",
            evaluated_packet_ref="pkg::001",
            required_gate_ids=("G21",),
            verdicts=verdicts,
        )
        assert mesh.get_verdict("G21") is not None
        assert mesh.get_verdict("G99") is None

    def test_gate_mesh_deterministic_digest_present(self):
        verdicts = (_verdict("G21", VERDICT_PASS),)
        mesh = build_gate_mesh_result(
            request_id="req", run_id="run", trace_root="trace",
            route_id="R5", evaluated_surface="managed_workflow",
            evaluated_packet_ref="pkg::001",
            required_gate_ids=("G21",),
            verdicts=verdicts,
        )
        assert len(mesh.deterministic_digest) == 64  # sha256 hex


# ── Gate Profile Resolver ─────────────────────────────────────────────────────

class TestGateProfileResolver:
    def test_apps_rg_gate_profile_resolves_required_exit_gates(self):
        resolver = GateProfileResolver(_REPO_ROOT)
        profile = resolver.resolve(
            exit_profile_path=(
                "apps_rg/config/domain_contract/"
                "exit_profile.resume_generation.v1.json"
            ),
            runtime_gate_profile_path=(
                "apps_rg/config/domain_contract/"
                "runtime_gate_profile.resume_generation.v1.json"
            ),
        )
        assert isinstance(profile.required_exit_gates, tuple)
        assert len(profile.required_exit_gates) > 0
        assert "G21" in profile.required_exit_gates
        assert "G22" in profile.required_exit_gates
        assert "G23" in profile.required_exit_gates
        assert "G24" in profile.required_exit_gates
        assert "G26" in profile.required_exit_gates
        assert "G28" in profile.required_exit_gates

    def test_apps_rg_exit_profile_resolves_g21_g28_rules(self):
        resolver = GateProfileResolver(_REPO_ROOT)
        profile = resolver.resolve(
            exit_profile_path=(
                "apps_rg/config/domain_contract/"
                "exit_profile.resume_generation.v1.json"
            ),
        )
        for gid in ("G21", "G22", "G23", "G24", "G25", "G26", "G27", "G28"):
            assert gid in profile.gate_definitions, f"Gate {gid} missing from profile"

    def test_apps_rg_conditional_gate_g27_is_not_required(self):
        resolver = GateProfileResolver(_REPO_ROOT)
        profile = resolver.resolve(
            exit_profile_path=(
                "apps_rg/config/domain_contract/"
                "exit_profile.resume_generation.v1.json"
            ),
        )
        assert "G27" not in profile.required_exit_gates
        assert "G27" in profile.conditional_exit_gates

    def test_gate_profile_resolver_fails_closed_on_missing_file(self, tmp_path: Path):
        resolver = GateProfileResolver(tmp_path)
        with pytest.raises(GateProfileError, match="Gate profile not found"):
            resolver.resolve(exit_profile_path="nonexistent/profile.json")

    def test_gate_profile_resolver_fails_closed_on_malformed_json(self, tmp_path: Path):
        bad = tmp_path / "exit_profile.json"
        bad.write_text("{not valid json", encoding="utf-8")
        resolver = GateProfileResolver(tmp_path)
        with pytest.raises(GateProfileError, match="malformed JSON"):
            resolver.resolve(exit_profile_path="exit_profile.json")

    def test_gate_profile_resolver_fails_closed_on_missing_required_key(self, tmp_path: Path):
        import json as _json
        bad = tmp_path / "exit_profile.json"
        bad.write_text(_json.dumps({"app_id": "test"}), encoding="utf-8")
        resolver = GateProfileResolver(tmp_path)
        with pytest.raises(GateProfileError, match="missing required key"):
            resolver.resolve(exit_profile_path="exit_profile.json")

    def test_profile_g22_dimension_thresholds_present(self):
        resolver = GateProfileResolver(_REPO_ROOT)
        profile = resolver.resolve(
            exit_profile_path=(
                "apps_rg/config/domain_contract/"
                "exit_profile.resume_generation.v1.json"
            ),
        )
        g22 = profile.gate_definitions.get("G22", {})
        thresholds = g22.get("dimension_thresholds", {})
        assert "no_fabrication" in thresholds
        assert "overall_pass_threshold" in thresholds
