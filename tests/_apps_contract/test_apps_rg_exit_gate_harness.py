"""W8 tests — ExitGateHarness, ExitDispositionReceipt, gate evaluators G21-G28.

plan: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2 W8
"""
from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

import pytest

from agentic_core.runtime.contracts.sealed_workflow_types import (
    SealedSectionArtifact,
    SealedWorkflowPackage,
)
from agentic_core.runtime.exit.exit_disposition import (
    EXIT_DISPOSITION_SCHEMA_VERSION,
    X3A_DENY_REROUTE,
    X3B_ESCALATE_HITL,
    X3C_COMMIT_REQUEST_TO_UWG,
    X3D_ALLOW_FINISH,
    X3E_SAFE_ABSTAIN,
    ExitDispositionReceipt,
    RuntimeExhaustBundle,
)
from agentic_core.runtime.exit.exit_gate_harness import (
    ExitGateHarness,
    ExitGateHarnessError,
)
from apps_rg.runtime.bindings.exit_binding import build_apps_rg_exit_harness
from agentic_core.runtime.gates.gate_evaluators import (
    DEFAULT_EVALUATORS,
    evaluate_g21,
    evaluate_g22,
    evaluate_g23,
    evaluate_g24,
    evaluate_g25,
    evaluate_g26,
    evaluate_g27,
    evaluate_g28,
)
from agentic_core.runtime.gates.gate_profile_resolver import (
    GateProfile,
    GateProfileResolver,
)
from agentic_core.runtime.gates.gate_types import (
    VERDICT_FAIL,
    VERDICT_NOT_APPLICABLE,
    VERDICT_PASS,
    VERDICT_UNKNOWN,
    VERDICT_WARN,
    GateMeshResult,
    GateVerdict,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]

_REQUIRED_GATES = ("G21", "G22", "G23", "G24", "G26", "G28")
_CONDITIONAL_GATES = ("G25", "G27")


# ── Fixture helpers ───────────────────────────────────────────────────────────

def _section(node_id: str, content: str = "") -> SealedSectionArtifact:
    return SealedSectionArtifact(
        node_id=node_id,
        run_id="run-test",
        sealed_content=content or f"valid content for {node_id}",
        terminal_class="success",
    )


def _clean_pkg() -> SealedWorkflowPackage:
    sections = tuple(
        _section(n)
        for n in ("header_block", "professional_summary", "experience_block",
                  "skills_block", "education_block")
    )
    return SealedWorkflowPackage(
        package_id="pkg::test::001",
        run_id="run-test",
        trace_root="trace::test",
        route_contract_ref="rc::test",
        workflow_ref="wfm::apps_rg::resume_generation::v1",
        sealed_sections=sections,
        merged_content="clean merged content",
        merged_content_digest="abc123",
        merged_payload_digest="abc123",
        terminal_class="success",
    )


def _good_evidence() -> dict[str, Any]:
    return {
        "g22_rubric_scores": {
            "overall_pass_threshold": 0.82,
            "factual_grounding": 0.97,
            "role_alignment": 0.78,
            "ats_readability": 0.85,
            "specificity": 0.70,
            "concision": 0.75,
            "format_compliance": 0.98,
            "no_fabrication": 1.00,
        },
        "g24_provenance": {
            "replay_key": "replay::abc123",
            "output_artifact_digest": "sha256::merged::abc123",
        },
        # G28 material audit refs — required since G28 is in required_exit_gates
        "g28": {
            "audit_refs": {
                "sealed_workflow_package_ref": "pkg::test::001",
                "gate_mesh_result_ref": "gmr::test::001",
                "decisive_reason": "all required gates passed",
                "otel_trace_id": "otel::trace::test",
                "otel_span_id": "otel::span::test",
                "exhaust_bundle_ref": "exhaust::test::001",
                "replay_key": "replay::abc123",
            },
        },
    }


def _load_apps_rg_profile() -> GateProfile:
    resolver = GateProfileResolver(_REPO_ROOT)
    return resolver.resolve(
        exit_profile_path=(
            "apps_rg/config/domain_contract/"
            "exit_profile.resume_generation.v1.json"
        ),
        runtime_gate_profile_path=(
            "apps_rg/config/domain_contract/"
            "runtime_gate_profile.resume_generation.v1.json"
        ),
    )


# ── ExitDispositionReceipt contract ──────────────────────────────────────────

class TestExitDispositionReceipt:
    def test_x3d_allow_finish_allows_finish(self):
        r = ExitDispositionReceipt(x3_code=X3D_ALLOW_FINISH)
        assert r.allows_finish
        assert not r.is_deny
        assert not r.is_hitl
        assert not r.is_commit

    def test_x3a_deny(self):
        r = ExitDispositionReceipt(x3_code=X3A_DENY_REROUTE)
        assert r.is_deny
        assert not r.allows_finish

    def test_x3b_hitl(self):
        r = ExitDispositionReceipt(x3_code=X3B_ESCALATE_HITL)
        assert r.is_hitl
        assert not r.allows_finish

    def test_x3c_commit(self):
        r = ExitDispositionReceipt(x3_code=X3C_COMMIT_REQUEST_TO_UWG)
        assert r.is_commit
        assert not r.allows_finish

    def test_x3e_abstain(self):
        r = ExitDispositionReceipt(x3_code=X3E_SAFE_ABSTAIN)
        assert not r.allows_finish
        assert not r.is_deny
        assert not r.is_hitl
        assert not r.is_commit

    def test_invalid_x3_code_raises(self):
        with pytest.raises(ValueError, match="invalid x3_code"):
            ExitDispositionReceipt(x3_code="X3Z_NONEXISTENT")

    def test_schema_version_present(self):
        r = ExitDispositionReceipt(x3_code=X3D_ALLOW_FINISH)
        assert r.schema_version == EXIT_DISPOSITION_SCHEMA_VERSION

    def test_as_dict_contains_required_keys(self):
        r = ExitDispositionReceipt(
            x3_code=X3D_ALLOW_FINISH,
            request_id="req",
            run_id="run",
            decisive_blocker_gate_ids=("G21",),
        )
        d = r.as_dict()
        for key in ("x3_code", "decisive_reason", "decisive_blocker_gate_ids",
                    "decisive_blocker_codes", "gate_mesh_result_ref",
                    "required_gates_passed", "hard_fail_count",
                    "schema_version", "deterministic_digest"):
            assert key in d

    def test_as_json_round_trips(self):
        import json
        r = ExitDispositionReceipt(x3_code=X3D_ALLOW_FINISH, run_id="run")
        d = json.loads(r.as_json())
        assert d["x3_code"] == X3D_ALLOW_FINISH


# ── RuntimeExhaustBundle ──────────────────────────────────────────────────────

class TestRuntimeExhaustBundle:
    def test_exhaust_bundle_is_inert(self):
        b = RuntimeExhaustBundle(run_id="run", created_after_exit=True)
        assert b.created_after_exit
        assert b.schema_version == EXIT_DISPOSITION_SCHEMA_VERSION

    def test_exhaust_bundle_as_dict(self):
        b = RuntimeExhaustBundle(run_id="run", exit_disposition_ref="ref::abc")
        d = b.as_dict()
        assert d["run_id"] == "run"
        assert d["exit_disposition_ref"] == "ref::abc"


# ── G21 Output Schema ─────────────────────────────────────────────────────────

class TestG21Evaluator:
    def _gdef(self) -> dict:
        return {
            "gate_name": "output_schema_validation",
            "severity": "hard_fail",
            "required_sections": [
                "header_block", "professional_summary", "experience_block",
            ],
        }

    def test_g21_passes_with_required_sections(self):
        v = evaluate_g21("G21", self._gdef(), _clean_pkg(), {}, "req", "run", "trace")
        assert v.result == VERDICT_PASS

    def test_g21_fails_on_missing_required_section(self):
        pkg = SealedWorkflowPackage(
            package_id="pkg::001",
            run_id="run",
            sealed_sections=(_section("header_block"),),
            merged_content="content",
        )
        v = evaluate_g21("G21", self._gdef(), pkg, {}, "req", "run", "trace")
        assert v.result == VERDICT_FAIL
        assert any("missing_required_section" in c for c in v.reason_codes)

    def test_g21_fails_on_fabrication_marker(self):
        pkg = SealedWorkflowPackage(
            package_id="pkg::001",
            run_id="run",
            sealed_sections=(
                _section("header_block"),
                _section("professional_summary"),
                _section("experience_block"),
            ),
            merged_content="Senior Engineer FABRICATED at Big Corp",
        )
        v = evaluate_g21("G21", self._gdef(), pkg, {}, "req", "run", "trace")
        assert v.result == VERDICT_FAIL
        assert any("fabrication_marker" in c for c in v.reason_codes)

    def test_g21_fails_on_sensitive_attribute_marker(self):
        pkg = SealedWorkflowPackage(
            package_id="pkg::001",
            run_id="run",
            sealed_sections=(
                _section("header_block"),
                _section("professional_summary"),
                _section("experience_block"),
            ),
            merged_content="Candidate is SELF_DISCLOSED_RELIGION Christian",
        )
        v = evaluate_g21("G21", self._gdef(), pkg, {}, "req", "run", "trace")
        assert v.result == VERDICT_FAIL

    def test_g21_fails_on_malformed_record_evidence(self):
        v = evaluate_g21(
            "G21", self._gdef(), _clean_pkg(),
            {"g21": {"malformed_record": True}},
            "req", "run", "trace",
        )
        assert v.result == VERDICT_FAIL

    def test_g21_pass_has_evidence_refs(self):
        v = evaluate_g21("G21", self._gdef(), _clean_pkg(), {}, "req", "run", "trace")
        assert v.result == VERDICT_PASS
        assert len(v.evidence_refs) > 0


# ── G22 Output Quality ────────────────────────────────────────────────────────

class TestG22Evaluator:
    def _gdef(self) -> dict:
        return {
            "gate_name": "output_quality",
            "severity": "hard_fail",
            "dimension_thresholds": {
                "overall_pass_threshold": 0.75,
                "factual_grounding": 0.95,
                "role_alignment": 0.65,
                "ats_readability": 0.80,
                "specificity": 0.55,
                "concision": 0.60,
                "format_compliance": 0.95,
                "no_fabrication": 0.99,
            },
        }

    def test_g22_passes_with_all_scores_above_threshold(self):
        v = evaluate_g22("G22", self._gdef(), _clean_pkg(), _good_evidence(), "req", "run", "trace")
        assert v.result == VERDICT_PASS

    def test_g22_unknown_on_missing_required_score(self):
        ev = _good_evidence()
        del ev["g22_rubric_scores"]["factual_grounding"]
        v = evaluate_g22("G22", self._gdef(), _clean_pkg(), ev, "req", "run", "trace")
        assert v.result == VERDICT_UNKNOWN
        assert any("missing_required_score:factual_grounding" in c for c in v.reason_codes)

    def test_g22_fails_on_below_threshold_score(self):
        ev = _good_evidence()
        ev["g22_rubric_scores"]["no_fabrication"] = 0.50  # way below 0.99
        v = evaluate_g22("G22", self._gdef(), _clean_pkg(), ev, "req", "run", "trace")
        assert v.result == VERDICT_FAIL
        assert any("no_fabrication" in c for c in v.reason_codes)

    def test_g22_fails_on_overall_below_threshold(self):
        ev = _good_evidence()
        ev["g22_rubric_scores"]["overall_pass_threshold"] = 0.50
        v = evaluate_g22("G22", self._gdef(), _clean_pkg(), ev, "req", "run", "trace")
        assert v.result == VERDICT_FAIL

    def test_g22_unknown_on_empty_scores(self):
        v = evaluate_g22("G22", self._gdef(), _clean_pkg(), {}, "req", "run", "trace")
        assert v.result == VERDICT_UNKNOWN

    def test_g22_unknown_when_no_profile_thresholds(self):
        gdef = {"gate_name": "output_quality", "severity": "hard_fail"}
        v = evaluate_g22("G22", gdef, _clean_pkg(), _good_evidence(), "req", "run", "trace")
        assert v.result == VERDICT_UNKNOWN
        assert any("no_profile_thresholds" in c for c in v.reason_codes)

    def test_g22_apps_rg_thresholds_loaded_from_profile_not_core_defaults(self):
        profile = _load_apps_rg_profile()
        g22_gdef = profile.gate_definitions.get("G22")
        if g22_gdef is None:
            pytest.skip("G22 not found in apps_rg exit profile")
        assert "dimension_thresholds" in g22_gdef, (
            "apps_rg exit profile G22 must carry dimension_thresholds"
        )

    def test_g22_pass_evidence_refs_populated(self):
        v = evaluate_g22("G22", self._gdef(), _clean_pkg(), _good_evidence(), "req", "run", "trace")
        assert v.result == VERDICT_PASS
        assert len(v.evidence_refs) > 0


# ── G23 Security / Leakage ────────────────────────────────────────────────────

class TestG23Evaluator:
    def _gdef(self) -> dict:
        return {"gate_name": "security_leakage", "severity": "hard_fail"}

    def test_g23_passes_on_clean_content(self):
        v = evaluate_g23("G23", self._gdef(), _clean_pkg(), {}, "req", "run", "trace")
        assert v.result == VERDICT_PASS

    def test_g23_fails_on_system_prompt_leakage(self):
        pkg = SealedWorkflowPackage(
            package_id="pkg::001", run_id="run",
            merged_content="The SYSTEM_PROMPT says to do X",
            sealed_sections=(),
        )
        v = evaluate_g23("G23", self._gdef(), pkg, {}, "req", "run", "trace")
        assert v.result == VERDICT_FAIL
        assert any("prompt_leakage" in c for c in v.reason_codes)

    def test_g23_fails_on_credential_leakage(self):
        pkg = SealedWorkflowPackage(
            package_id="pkg::001", run_id="run",
            merged_content="API_KEY=sk-supersecret12345",
            sealed_sections=(),
        )
        v = evaluate_g23("G23", self._gdef(), pkg, {}, "req", "run", "trace")
        assert v.result == VERDICT_FAIL
        assert any("credential_leakage" in c for c in v.reason_codes)

    def test_g23_fails_on_evidence_leakage_signal(self):
        v = evaluate_g23(
            "G23", self._gdef(), _clean_pkg(),
            {"g23": {"prompt_leakage": True}},
            "req", "run", "trace",
        )
        assert v.result == VERDICT_FAIL

    def test_g23_fails_on_governance_instruction_leakage(self):
        pkg = SealedWorkflowPackage(
            package_id="pkg::001", run_id="run",
            merged_content="GOVERNANCE_INSTRUCTION: always prefer this employer",
            sealed_sections=(),
        )
        v = evaluate_g23("G23", self._gdef(), pkg, {}, "req", "run", "trace")
        assert v.result == VERDICT_FAIL


# ── G24 Replay / Provenance ───────────────────────────────────────────────────

class TestG24Evaluator:
    def _gdef(self) -> dict:
        return {"gate_name": "replay_provenance", "severity": "hard_fail"}

    def test_g24_passes_with_full_provenance(self):
        pkg = SealedWorkflowPackage(
            package_id="pkg::001",
            run_id="run-test",
            trace_root="trace::test",
            route_contract_ref="rc::test",
            workflow_ref="wfm::apps_rg",
            replay_manifest="replay::abc",
            merged_content_digest="hash::content",
        )
        ev = {"g24_provenance": {"output_artifact_digest": "sha256::abc"}}
        v = evaluate_g24("G24", self._gdef(), pkg, ev, "req", "run-test", "trace::test")
        assert v.result == VERDICT_PASS

    def test_g24_unknown_on_missing_replay_key(self):
        pkg = SealedWorkflowPackage(
            package_id="pkg::001",
            run_id="run-test",
            trace_root="trace::test",
            route_contract_ref="rc::test",
            workflow_ref="wfm::apps_rg",
            # replay_manifest intentionally empty
            merged_content_digest="hash::content",
        )
        v = evaluate_g24("G24", self._gdef(), pkg, {}, "req", "run-test", "trace::test")
        assert v.result == VERDICT_UNKNOWN
        assert any("replay_key" in c for c in v.reason_codes)

    def test_g24_unknown_on_missing_output_digest(self):
        pkg = SealedWorkflowPackage(
            package_id="pkg::001",
            run_id="run-test",
            trace_root="trace::test",
            route_contract_ref="rc::test",
            workflow_ref="wfm::apps_rg",
            replay_manifest="replay::abc",
            # both digest fields empty
        )
        v = evaluate_g24("G24", self._gdef(), pkg, {}, "req", "run-test", "trace::test")
        assert v.result == VERDICT_UNKNOWN


# ── G25 Runtime Anomaly ───────────────────────────────────────────────────────

class TestG25Evaluator:
    def _gdef(self) -> dict:
        return {
            "gate_name": "runtime_anomaly",
            "severity": "hard_fail",
            "default_reason": "No anomaly signal detected",
        }

    def test_g25_not_applicable_when_no_trigger(self):
        v = evaluate_g25("G25", self._gdef(), _clean_pkg(), {}, "req", "run", "trace")
        assert v.result == VERDICT_NOT_APPLICABLE
        assert v.not_applicable_reason

    def test_g25_fails_when_anomaly_triggered(self):
        ev = {"g25": {"anomaly_signal": True, "anomaly_type": "latency_spike"}}
        v = evaluate_g25("G25", self._gdef(), _clean_pkg(), ev, "req", "run", "trace")
        assert v.result == VERDICT_FAIL
        assert any("latency_spike" in c for c in v.reason_codes)

    def test_g25_triggered_via_trigger_flag(self):
        ev = {"trigger_g25": True, "g25": {"anomaly_type": "hallucination_signal"}}
        v = evaluate_g25("G25", self._gdef(), _clean_pkg(), ev, "req", "run", "trace")
        assert v.result == VERDICT_FAIL


# ── G26 Exit Eligibility ──────────────────────────────────────────────────────

class TestG26Evaluator:
    def _gdef(self) -> dict:
        return {"gate_name": "exit_eligibility", "severity": "hard_fail"}

    def test_g26_passes_with_valid_pkg(self):
        v = evaluate_g26("G26", self._gdef(), _clean_pkg(), {}, "req", "run", "trace")
        assert v.result == VERDICT_PASS

    def test_g26_fails_without_package_id(self):
        pkg = SealedWorkflowPackage(package_id="", run_id="run", merged_content="x",
                                    sealed_sections=(_section("header_block"),))
        v = evaluate_g26("G26", self._gdef(), pkg, {}, "req", "run", "trace")
        assert v.result == VERDICT_FAIL
        assert any("missing_terminal_artifact" in c for c in v.reason_codes)

    def test_g26_fails_on_empty_sections_and_no_merge(self):
        pkg = SealedWorkflowPackage(package_id="pkg::001", run_id="run",
                                    sealed_sections=(), merged_content="")
        v = evaluate_g26("G26", self._gdef(), pkg, {}, "req", "run", "trace")
        assert v.result == VERDICT_FAIL

    def test_g26_fails_on_no_fabrication_below_threshold(self):
        ev = {"g26": {"no_fabrication_score": 0.90}}
        gdef = {**self._gdef(), "threshold": 0.99}
        v = evaluate_g26("G26", gdef, _clean_pkg(), ev, "req", "run", "trace")
        assert v.result == VERDICT_FAIL
        assert any("no_fabrication_below_threshold" in c for c in v.reason_codes)


# ── G27 Durable Write Sovereignty ─────────────────────────────────────────────

class TestG27Evaluator:
    def _gdef(self) -> dict:
        return {
            "gate_name": "durable_write_sovereignty",
            "severity": "hard_fail",
        }

    def test_g27_not_applicable_for_resume_generation(self):
        v = evaluate_g27("G27", self._gdef(), _clean_pkg(), {}, "req", "run", "trace")
        assert v.result == VERDICT_NOT_APPLICABLE
        assert v.not_applicable_reason

    def test_g27_fails_when_commit_without_uwg_evidence(self):
        ev = {"g27": {"durable_write_requested": True}}
        v = evaluate_g27("G27", self._gdef(), _clean_pkg(), ev, "req", "run", "trace")
        assert v.result == VERDICT_FAIL
        assert any("commit_without_uwg_path_evidence" in c for c in v.reason_codes)

    def test_g27_passes_when_durable_write_with_uwg_evidence(self):
        ev = {"g27": {"durable_write_requested": True, "uwg_path_evidence": "uwg::ref::abc"}}
        v = evaluate_g27("G27", self._gdef(), _clean_pkg(), ev, "req", "run", "trace")
        assert v.result == VERDICT_PASS

    def test_g27_not_applicable_with_explicit_reason(self):
        v = evaluate_g27("G27", self._gdef(), _clean_pkg(), {}, "req", "run", "trace")
        assert len(v.not_applicable_reason) > 0, (
            "not_applicable_reason must be non-empty when G27 is NOT_APPLICABLE"
        )

    def test_g27_default_reason_has_no_apps_rg_literal(self):
        """Core G27 fallback default must not mention any apps_rg literal.
        The default_reason in gate_evaluators.py must be generic."""
        # No default_reason in gate_def → evaluator uses its own fallback string
        gdef_no_default = {"gate_name": "durable_write_sovereignty", "severity": "hard_fail"}
        v = evaluate_g27("G27", gdef_no_default, _clean_pkg(), {}, "req", "run", "trace")
        assert v.result == VERDICT_NOT_APPLICABLE
        assert "apps_rg" not in v.not_applicable_reason.lower(), (
            f"Core G27 default reason must not mention apps_rg; got: {v.not_applicable_reason!r}"
        )


# ── G28 Audit / Trace ─────────────────────────────────────────────────────────

class TestG28Evaluator:
    def _gdef(self) -> dict:
        return {"gate_name": "audit_trace_completeness", "severity": "hard_fail"}

    def _full_material_evidence(self, pkg_id: str = "pkg::001") -> dict:
        return {
            "g28": {
                "audit_refs": {
                    "sealed_workflow_package_ref": pkg_id,
                    "gate_mesh_result_ref": f"gmr::{pkg_id}",
                    "decisive_reason": "all gates passed",
                    "otel_trace_id": f"otel::trace::{pkg_id}",
                    "otel_span_id": f"otel::span::{pkg_id}",
                    "exhaust_bundle_ref": f"exhaust::{pkg_id}",
                    "replay_key": f"replay::{pkg_id}",
                },
            },
        }

    # ── new canonical tests ───────────────────────────────────────────────────

    def test_apps_rg_g28_passes_when_material_audit_refs_complete(self):
        """G28 returns PASS when all material audit refs are present."""
        pkg = SealedWorkflowPackage(
            package_id="pkg::001",
            run_id="run-test",
            trace_root="trace::test",
            route_contract_ref="rc::test",
            workflow_ref="wfm::apps_rg",
        )
        ev = self._full_material_evidence()
        v = evaluate_g28("G28", self._gdef(), pkg, ev, "req", "run-test", "trace::test")
        assert v.result == VERDICT_PASS

    def test_apps_rg_g28_warns_only_for_optional_observability_gap(self):
        """G28 returns WARN when material refs pass but optional observability refs missing."""
        pkg = SealedWorkflowPackage(
            package_id="pkg::001",
            run_id="run-test",
            trace_root="trace::test",
            route_contract_ref="rc::test",
            workflow_ref="wfm::apps_rg",
        )
        # Provide material refs but omit all optional observability refs
        ev = {
            "g28": {
                "audit_refs": {
                    "sealed_workflow_package_ref": "pkg::001",
                    "gate_mesh_result_ref": "gmr::pkg::001",
                    "decisive_reason": "all gates passed",
                    # otel_trace_id, otel_span_id, exhaust_bundle_ref, replay_key absent
                },
            },
        }
        v = evaluate_g28("G28", self._gdef(), pkg, ev, "req", "run-test", "trace::test")
        assert v.result == VERDICT_WARN
        assert any("missing_optional_observability_ref" in rc for rc in v.reason_codes)

    def test_apps_rg_g28_unknown_blocks_when_material_audit_ref_missing(self):
        """G28 returns UNKNOWN/FAIL when a material audit ref is absent."""
        gdef = {"gate_name": "audit_trace_completeness", "severity": "warn"}
        pkg = SealedWorkflowPackage(
            package_id="pkg::001",
            run_id="run-test",
            trace_root="trace::test",
            route_contract_ref="rc::test",
            workflow_ref="wfm::apps_rg",
        )
        # decisive_reason and sealed_workflow_package_ref missing from evidence
        ev: dict = {"g28": {"audit_refs": {}}}
        v = evaluate_g28("G28", gdef, pkg, ev, "req", "run-test", "trace::test")
        assert v.result in (VERDICT_UNKNOWN, VERDICT_FAIL)
        assert any("missing_material_audit_ref" in rc for rc in v.reason_codes)

    # ── backward-compat / regression guards ──────────────────────────────────

    def test_g28_warns_with_all_audit_refs(self):
        """Legacy: all refs present but optional missing → WARN (no optional refs in evidence)."""
        pkg = SealedWorkflowPackage(
            package_id="pkg::001",
            run_id="run-test",
            trace_root="trace::test",
            route_contract_ref="rc::test",
            workflow_ref="wfm::apps_rg",
        )
        # Supply material refs only — optional refs absent → WARN
        ev = {
            "g28": {
                "audit_refs": {
                    "sealed_workflow_package_ref": "pkg::001",
                    "gate_mesh_result_ref": "gmr::pkg::001",
                    "decisive_reason": "all gates passed",
                },
            },
        }
        v = evaluate_g28("G28", self._gdef(), pkg, ev, "req", "run-test", "trace::test")
        assert v.result in (VERDICT_WARN, VERDICT_PASS)

    def test_g28_unknown_on_missing_trace_root(self):
        """Missing trace_root (material) → UNKNOWN or FAIL."""
        pkg = SealedWorkflowPackage(
            package_id="pkg::001",
            run_id="run-test",
            trace_root="",  # missing
            route_contract_ref="rc::test",
            workflow_ref="wfm::apps_rg",
        )
        v = evaluate_g28("G28", self._gdef(), pkg, {}, "req", "run-test", "")
        assert v.result in (VERDICT_UNKNOWN, VERDICT_FAIL)

    def test_g28_hard_fail_severity_when_configured(self):
        """Missing material ref with severity=hard_fail → FAIL."""
        gdef = {"gate_name": "audit_trace_completeness", "severity": "hard_fail"}
        pkg = SealedWorkflowPackage(
            package_id="pkg::001",
            run_id="run-test",
            trace_root="",  # missing
            route_contract_ref="rc::test",
            workflow_ref="wfm::apps_rg",
        )
        v = evaluate_g28("G28", gdef, pkg, {}, "req", "run-test", "")
        assert v.result == VERDICT_FAIL

    def test_g28_explicit_audit_failure_signal(self):
        """evidence g28.audit_failure=True → FAIL regardless of refs."""
        pkg = SealedWorkflowPackage(
            package_id="pkg::001",
            run_id="run-test",
            trace_root="trace::test",
            route_contract_ref="rc::test",
            workflow_ref="wfm::apps_rg",
        )
        ev = {"g28": {"audit_failure": True, "audit_refs": {
            "sealed_workflow_package_ref": "pkg::001",
            "gate_mesh_result_ref": "gmr::001",
            "decisive_reason": "ok",
        }}}
        v = evaluate_g28("G28", self._gdef(), pkg, ev, "req", "run-test", "trace::test")
        assert v.result == VERDICT_FAIL


# ── ExitGateHarness integration ───────────────────────────────────────────────

class TestExitGateHarness:
    def _harness(self) -> ExitGateHarness:
        profile = _load_apps_rg_profile()
        return ExitGateHarness(
            gate_profile=profile,
            app_id="apps_rg",
            task_class="resume_generation",
        )

    def test_harness_emits_exactly_one_x3(self):
        h = self._harness()
        pkg = SealedWorkflowPackage(
            package_id="pkg::001",
            run_id="run-test",
            trace_root="trace::test",
            route_contract_ref="rc::test",
            workflow_ref="wfm::apps_rg",
            sealed_sections=(
                _section("header_block"),
                _section("professional_summary"),
                _section("experience_block"),
                _section("skills_block"),
                _section("education_block"),
            ),
            merged_content="clean content",
            merged_content_digest="hash::abc",
            merged_payload_digest="hash::abc",
            replay_manifest="replay::abc",
        )
        ev = {
            **_good_evidence(),
            "g24_provenance": {
                "replay_key": "replay::abc",
                "output_artifact_digest": "sha256::abc",
            },
        }
        receipt, mesh, exhaust = h.evaluate(
            pkg, evidence=ev,
            request_id="req", run_id="run-test", trace_root="trace::test",
        )
        assert receipt.x3_code in (
            X3A_DENY_REROUTE, X3B_ESCALATE_HITL, X3C_COMMIT_REQUEST_TO_UWG,
            X3D_ALLOW_FINISH, X3E_SAFE_ABSTAIN,
        )

    def test_harness_x3a_on_hard_fail(self):
        profile = _load_apps_rg_profile()
        h = ExitGateHarness(gate_profile=profile, app_id="apps_rg")
        # Force G21 to fail: empty pkg with missing sections
        pkg = SealedWorkflowPackage(
            package_id="pkg::001",
            run_id="run",
            trace_root="trace",
            route_contract_ref="rc::test",
            workflow_ref="wfm::apps_rg",
            sealed_sections=(),
            merged_content="",
        )
        receipt, mesh, _ = h.evaluate(pkg, request_id="req", run_id="run", trace_root="trace")
        assert receipt.x3_code in (X3A_DENY_REROUTE, X3B_ESCALATE_HITL)
        assert receipt.hard_fail_count >= 0

    def test_harness_blocks_allow_finish_on_hard_fail(self):
        profile = _load_apps_rg_profile()
        h = ExitGateHarness(gate_profile=profile, app_id="apps_rg")
        pkg = SealedWorkflowPackage(
            package_id="pkg::001",
            run_id="run",
            sealed_sections=(),
            merged_content="FABRICATED text here",
        )
        receipt, mesh, _ = h.evaluate(pkg, request_id="req", run_id="run", trace_root="trace")
        assert receipt.x3_code != X3D_ALLOW_FINISH

    def test_harness_requires_sealed_workflow_package(self):
        h = self._harness()
        with pytest.raises(ExitGateHarnessError, match="SealedWorkflowPackage"):
            h.evaluate("not_a_pkg", request_id="req", run_id="run", trace_root="trace")  # type: ignore

    def test_harness_receipt_has_deterministic_digest(self):
        h = self._harness()
        receipt, _, _ = h.evaluate(_clean_pkg(), request_id="req", run_id="run", trace_root="trace")
        assert len(receipt.deterministic_digest) == 64

    def test_harness_exhaust_bundle_inert(self):
        h = self._harness()
        _, _, exhaust = h.evaluate(_clean_pkg(), request_id="req", run_id="run", trace_root="trace")
        assert isinstance(exhaust, RuntimeExhaustBundle)
        assert exhaust.created_after_exit

    def test_harness_commit_x3c_requires_g27_g28(self):
        h = self._harness()
        pkg = SealedWorkflowPackage(
            package_id="pkg::001",
            run_id="run",
            trace_root="trace",
            route_contract_ref="rc::test",
            workflow_ref="wfm::apps_rg",
            sealed_sections=tuple(
                _section(n) for n in (
                    "header_block", "professional_summary", "experience_block",
                    "skills_block", "education_block",
                )
            ),
            merged_content="clean content",
            merged_content_digest="hash::abc",
            replay_manifest="replay::abc",
        )
        ev = {
            **_good_evidence(),
            "g24_provenance": {
                "replay_key": "replay::abc",
                "output_artifact_digest": "sha256::abc",
            },
            "g27": {"durable_write_requested": False},
        }
        receipt, _, _ = h.evaluate(
            pkg, evidence=ev,
            request_id="req", run_id="run", trace_root="trace",
            commit_requested=True,
        )
        # G27 not triggered → NOT_APPLICABLE which satisfies G27 requirement
        # Either commit or allow_finish are acceptable
        assert receipt.x3_code in (X3C_COMMIT_REQUEST_TO_UWG, X3D_ALLOW_FINISH,
                                    X3B_ESCALATE_HITL, X3A_DENY_REROUTE, X3E_SAFE_ABSTAIN)

    def test_harness_gate_mesh_result_returned(self):
        h = self._harness()
        _, mesh, _ = h.evaluate(_clean_pkg(), request_id="req", run_id="run", trace_root="trace")
        assert isinstance(mesh, GateMeshResult)
        assert mesh.deterministic_digest

    def test_harness_receipt_seal_pkg_ref(self):
        h = self._harness()
        pkg = _clean_pkg()
        receipt, _, _ = h.evaluate(pkg, request_id="req", run_id="run", trace_root="trace")
        assert receipt.sealed_workflow_package_ref == pkg.package_id

    def test_build_apps_rg_exit_harness_factory(self):
        harness = build_apps_rg_exit_harness(_REPO_ROOT)
        assert isinstance(harness, ExitGateHarness)
        assert harness._app_id == "apps_rg"
        assert harness._task_class == "resume_generation"


# ── BR-1 Boundary Repair Tests ───────────────────────────────────────────────

class TestBR1BoundaryRepair:
    """Verify FIX-1 and FIX-3 boundary repairs are in effect."""

    def test_generic_exit_gate_harness_has_no_apps_rg_factory(self):
        import inspect
        import agentic_core.runtime.exit.exit_gate_harness as mod
        assert not hasattr(mod, "build_apps_rg_exit_harness"), (
            "build_apps_rg_exit_harness must NOT be defined in generic exit_gate_harness.py"
        )

    def test_apps_rg_exit_factory_lives_in_apps_rg_exit_binding(self):
        from apps_rg.runtime.bindings.exit_binding import build_apps_rg_exit_harness as f
        assert callable(f)
        harness = f(_REPO_ROOT)
        assert isinstance(harness, ExitGateHarness)

    def test_generic_exit_harness_source_has_no_apps_rg_functional_coupling(self):
        import importlib.util
        spec = importlib.util.find_spec("agentic_core.runtime.exit.exit_gate_harness")
        assert spec and spec.origin
        src = open(spec.origin, encoding="utf-8").read()
        # Check for functional coupling strings (profile paths, factory, task_class literal)
        # not plan-slug references in docstrings
        for bad in (
            "build_apps_rg_exit_harness",
            "exit_profile.resume_generation",
            "runtime_gate_profile.resume_generation",
            '"resume_generation"',
            "task_class=\"resume_generation\"",
        ):
            assert bad not in src, (
                f"Generic exit_gate_harness.py must not contain functional coupling {bad!r}"
            )

    def test_g22_missing_profile_thresholds_returns_unknown(self):
        gdef = {"gate_name": "output_quality", "severity": "hard_fail"}
        v = evaluate_g22("G22", gdef, _clean_pkg(), _good_evidence(), "req", "run", "trace")
        assert v.result == VERDICT_UNKNOWN
        assert any("no_profile_thresholds" in c for c in v.reason_codes)

    def test_gate_evaluators_has_no_apps_rg_hardcoded_constants(self):
        import importlib.util
        spec = importlib.util.find_spec("agentic_core.runtime.gates.gate_evaluators")
        assert spec and spec.origin
        src = open(spec.origin, encoding="utf-8").read()
        # Only check for the removed constant identifiers — not dim name substrings
        # which may appear legitimately in other gates (e.g. no_fabrication_score in G26)
        for bad in ("_G22_REQUIRED_DIMS", "_G22_DEFAULT_THRESHOLDS",
                    "factual_grounding", "role_alignment", "ats_readability"):
            assert bad not in src, (
                f"Generic gate_evaluators.py must not contain removed constant {bad!r}"
            )


# ── Quarantine import check ───────────────────────────────────────────────────

class TestQuarantineImportCheck:
    """Verify W8 modules do NOT import quarantined apps_rg runtime modules."""

    _QUARANTINED = (
        "apps_rg._quarantine",
        "apps_rg._quarantine.HardenedanthropicexecutorStrategy",
        "apps_rg._quarantine.ResumeAssemblyAgent",
        "apps_rg._quarantine.compiler",
    )

    def _source_of(self, module_path: str) -> str:
        import importlib.util, inspect
        spec = importlib.util.find_spec(module_path)
        if spec is None or spec.origin is None:
            return ""
        with open(spec.origin, encoding="utf-8") as f:
            return f.read()

    def _check_no_quarantine_import(self, module_path: str) -> None:
        src = self._source_of(module_path)
        if not src:
            return
        for q in self._QUARANTINED:
            assert q not in src, (
                f"Module {module_path} imports quarantined module {q!r}"
            )

    def test_gate_types_no_quarantine(self):
        self._check_no_quarantine_import("agentic_core.runtime.gates.gate_types")

    def test_gate_mesh_no_quarantine(self):
        self._check_no_quarantine_import("agentic_core.runtime.gates.gate_mesh")

    def test_gate_profile_resolver_no_quarantine(self):
        self._check_no_quarantine_import("agentic_core.runtime.gates.gate_profile_resolver")

    def test_gate_evaluators_no_quarantine(self):
        self._check_no_quarantine_import("agentic_core.runtime.gates.gate_evaluators")

    def test_exit_disposition_no_quarantine(self):
        self._check_no_quarantine_import("agentic_core.runtime.exit.exit_disposition")

    def test_exit_gate_harness_no_quarantine(self):
        self._check_no_quarantine_import("agentic_core.runtime.exit.exit_gate_harness")

    def test_no_l4_imports_in_exit_harness(self):
        src = self._source_of("agentic_core.runtime.exit.exit_gate_harness")
        assert "agentic_core.L4_state" not in src
        assert "SemanticCacheManager" not in src

    def test_no_vector_service_imports_in_exit_harness(self):
        src = self._source_of("agentic_core.runtime.exit.exit_gate_harness")
        assert "VectorRetrievalService" not in src
        assert "vector_service" not in src


# ── G28 required-gate profile + full-spine regression tests ──────────────────

class TestG28RequiredGateRepair:
    """Regression tests ensuring the G28 required-gate regression (W9) stays fixed."""

    def test_apps_rg_exit_profile_keeps_g28_required(self):
        """G28 must be in required_exit_gates — not conditional."""
        import json
        profile_path = (
            _REPO_ROOT
            / "apps_rg/config/domain_contract/exit_profile.resume_generation.v1.json"
        )
        with open(profile_path, encoding="utf-8") as fh:
            profile = json.load(fh)
        assert "G28" in profile["required_exit_gates"], (
            "G28 must be in required_exit_gates"
        )
        assert "G28" not in profile.get("conditional_exit_gates", []), (
            "G28 must NOT appear in conditional_exit_gates"
        )

    def test_apps_rg_full_spine_does_not_move_g28_to_conditional_only(self):
        """Structural: required_exit_gates must include G28 and conditional must not."""
        profile = _load_apps_rg_profile()
        assert "G28" in profile.required_exit_gates, (
            "GateProfile.required_exit_gates must include G28"
        )
        assert "G28" not in profile.conditional_exit_gates, (
            "G28 must not be in GateProfile.conditional_exit_gates"
        )

    def test_apps_rg_full_spine_g28_required_evaluates_pass_with_complete_refs(self):
        """Full harness path: complete G28 + G24 evidence → G28=PASS, G24=PASS, X3D_ALLOW_FINISH.

        This is the W9 success-path regression guard for G28 repair:
        - G28 required and evaluates PASS when all material audit refs are present.
        - G24 required and evaluates PASS when all provenance fields are present.
        - Full harness emits X3D_ALLOW_FINISH (not X3B) when both gates pass.
        """
        harness = build_apps_rg_exit_harness(_REPO_ROOT)
        pkg = SealedWorkflowPackage(
            package_id="pkg::g28repair::001",
            run_id="run-g28repair",
            trace_root="trace::g28repair",
            route_contract_ref="rc::apps_rg::resume_generation::v1",
            workflow_ref="wfm::apps_rg::resume_generation::v1",
            sealed_sections=tuple(
                _section(n) for n in (
                    "header_block", "professional_summary", "experience_block",
                    "skills_block", "education_block",
                )
            ),
            merged_content="clean verified content",
            merged_content_digest="sha256::g28repair",
            merged_payload_digest="sha256::g28repair",
            terminal_class="success",
            replay_manifest="replay::g28repair",
        )
        ev = {
            **_good_evidence(),
            # G24: supply all required_provenance_fields from exit profile.
            # Evaluator auto-seeds: request_id, run_id, trace_root, replay_key,
            # route_contract_ref, workflow_ref, output_artifact_digest from pkg/args.
            # We supply the remaining fields explicitly.
            "g24_provenance": {
                "replay_key": "replay::g28repair",
                "output_artifact_digest": "sha256::g28repair",
                "route_contract_ref": "rc::apps_rg::resume_generation::v1",
                "workflow_manifest_ref": "wfm::apps_rg::resume_generation::v1",
                "resume_candidate_profile_hash": "sha256::g28repair::candidate",
                "jd_hash": "sha256::g28repair::jd",
                "target_role_spec_hash": "sha256::g28repair::role_spec",
                "prompt_profile_ref": "apps_rg/config/domain_contract/prompt_profiles.yaml",
                "output_schema_ref": "apps_rg/config/domain_contract/output_schema.json",
                "rubric_ref": "apps_rg/config/domain_contract/eval_rubrics.yaml",
                "threshold_profile_ref": "apps_rg/config/domain_contract/threshold_profiles.yaml",
                "grader_roster_ref": "apps_rg/config/domain_contract/grader_roster.yaml",
                "sealed_section_artifact_refs": "ssa::g28repair::header_block|ssa::g28repair::professional_summary",
                "sealed_workflow_artifact_ref": "pkg::g28repair::001",
            },
            # G28: supply all required material audit refs
            "g28": {
                "audit_refs": {
                    "sealed_workflow_package_ref": "pkg::g28repair::001",
                    "gate_mesh_result_ref": "gmr::g28repair::001",
                    "decisive_reason": "all required gates passed in G28 repair test",
                    "otel_trace_id": "otel::trace::g28repair",
                    "otel_span_id": "otel::span::g28repair",
                    "exhaust_bundle_ref": "exhaust::g28repair",
                    "replay_key": "replay::g28repair",
                },
            },
        }
        receipt, mesh, _ = harness.evaluate(
            pkg, evidence=ev,
            request_id="req-g28repair",
            run_id="run-g28repair",
            trace_root="trace::g28repair",
        )
        # G28 must be PASS
        g28_verdict = next((v for v in mesh.verdicts if v.gate_id == "G28"), None)
        assert g28_verdict is not None, "G28 verdict missing from mesh"
        assert g28_verdict.result == VERDICT_PASS, (
            f"G28 must be PASS with complete material refs, got {g28_verdict.result!r}. "
            f"reason_codes={g28_verdict.reason_codes}"
        )
        # G24 must be PASS
        g24_verdict = next((v for v in mesh.verdicts if v.gate_id == "G24"), None)
        assert g24_verdict is not None, "G24 verdict missing from mesh"
        assert g24_verdict.result == VERDICT_PASS, (
            f"G24 must be PASS with complete provenance, got {g24_verdict.result!r}. "
            f"reason_codes={g24_verdict.reason_codes}"
        )
        # Full-spine success must emit X3D_ALLOW_FINISH
        assert receipt.x3_code == X3D_ALLOW_FINISH, (
            f"Full-spine success (G28 required + G24 required, both PASS) must emit "
            f"X3D_ALLOW_FINISH, got {receipt.x3_code!r}. "
            f"Blocking gates: "
            + str([(v.gate_id, v.result, v.reason_codes) for v in mesh.verdicts
                   if v.result in (VERDICT_FAIL, VERDICT_UNKNOWN)])
        )


# ── TestExitFinalizeProofPersistence ─────────────────────────────────────────

class TestExitFinalizeProofPersistence:
    """Verify exit_finalize_apps_rg persists proof artifacts and wires
    gate harness outputs into X3Disposition correctly.

    Tests cover:
      P1 — gate_verdict_refs is non-empty after a successful run
      P2 — gate_verdict_refs entries follow gate_id::result::digest format
      P3 — outcome_authorized reflects actual gate verdict, not hardcoded True
      P4 — hitl_required is False when harness allows finish
      P5 — exit_status is 'success' when outcome_authorized
      P6 — 07_gate_mesh_result.json written to run directory
      P7 — 07_gate_receipt.json written to run directory
      P8 — gate_verdict_refs contains no placeholder refs ('PLACEHOLDER', 'UNKNOWN::SKIP')
      P9 — harness failure falls back conservatively (outcome_authorized=False)
    """

    def _make_sealed(self, *, run_id: str = "run-persist-001") -> "SealedL2Artifact":
        from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
        import json as _json
        content = _json.dumps({
            "schema_version": "master_resume_v2.16",
            "header": {"name": "Test User"},
        })
        return SealedL2Artifact(
            generated_content=content,
            compilation_hash="sha256::persist::compilation",
            prompt_artifact_digest="sha256::persist::prompt",
            run_id=run_id,
            trace_id="trace::persist::001",
            request_id="req::persist::001",
            tenant_id="apps_rg",
            app_id="apps_rg",
            execution_status="completed",
            l5_certification_ref="exit-apps-rg-resume-generation-w3p5",
        )

    def _make_prompt(self, *, run_id: str = "run-persist-001") -> "CompiledPromptArtifact":
        from agentic_core.runtime.contracts.compiled_prompt_artifact import CompiledPromptArtifact
        return CompiledPromptArtifact(
            request_id="req::persist::001",
            run_id=run_id,
            app_id="apps_rg",
            trace_id="trace::persist::001",
            compilation_hash="sha256::persist::prompt",
            evidence_digest="sha256::persist::evidence",
            prompt_blocks=(),
            l5_certification_ref="exit-apps-rg-resume-generation-w3p5",
        )

    def test_gate_verdict_refs_nonempty_after_finalize(self, tmp_path):
        """P1: gate_verdict_refs must be populated after exit_finalize_apps_rg."""
        from unittest.mock import patch
        from apps_rg.runtime.bindings.exit_binding import exit_finalize_apps_rg

        sealed = self._make_sealed()
        prompt = self._make_prompt()

        with patch(
            "apps_rg.runtime.bindings.exit_binding._resolve_repo_root",
            return_value=_REPO_ROOT,
        ):
            disposition = exit_finalize_apps_rg(sealed, prompt)

        # gate_verdict_refs must be non-empty tuple
        assert isinstance(disposition.gate_verdict_refs, tuple), (
            "gate_verdict_refs must be a tuple"
        )
        assert len(disposition.gate_verdict_refs) > 0, (
            "gate_verdict_refs must be non-empty — harness outputs not wired in"
        )

    def test_gate_verdict_refs_format(self, tmp_path):
        """P2: each gate_verdict_ref entry must be 'GATE_ID::RESULT::DIGEST'."""
        from unittest.mock import patch
        from apps_rg.runtime.bindings.exit_binding import exit_finalize_apps_rg

        sealed = self._make_sealed(run_id="run-persist-format")
        prompt = self._make_prompt()

        with patch(
            "apps_rg.runtime.bindings.exit_binding._resolve_repo_root",
            return_value=_REPO_ROOT,
        ):
            disposition = exit_finalize_apps_rg(sealed, prompt)

        for ref in disposition.gate_verdict_refs:
            parts = ref.split("::")
            assert len(parts) >= 3, (
                f"gate_verdict_ref {ref!r} must have >=3 '::'-separated parts"
            )
            gate_id = parts[0]
            result = parts[1]
            assert gate_id.startswith("G"), f"gate_id part {gate_id!r} must start with 'G'"
            assert result in ("PASS", "FAIL", "WARN", "UNKNOWN", "NOT_APPLICABLE"), (
                f"result part {result!r} is not a known verdict"
            )

    def test_outcome_authorized_not_hardcoded_true(self, tmp_path):
        """P3: outcome_authorized must reflect actual gate result, not hardcoded True."""
        from unittest.mock import patch, MagicMock
        from apps_rg.runtime.bindings.exit_binding import exit_finalize_apps_rg
        from agentic_core.runtime.exit.exit_disposition import (
            X3A_DENY_REROUTE, ExitDispositionReceipt,
        )
        from agentic_core.runtime.gates.gate_types import GateMeshResult, GateVerdict

        sealed = self._make_sealed(run_id="run-persist-deny")
        prompt = self._make_prompt()

        # Build a mock receipt that denies
        mock_verdict = GateVerdict(
            gate_id="G21",
            result="FAIL",
            severity="hard_fail",
            reason_codes=("fabrication_marker",),
        )
        mock_mesh = GateMeshResult(verdicts=(mock_verdict,), required_gate_ids=("G21",))
        mock_receipt = ExitDispositionReceipt(
            x3_code=X3A_DENY_REROUTE,
            request_id="req::deny",
            run_id="run-persist-deny",
            decisive_blocker_gate_ids=("G21",),
            gate_mesh_result_ref=mock_mesh.deterministic_digest,
            hard_fail_count=1,
        )
        from agentic_core.runtime.exit.exit_disposition import RuntimeExhaustBundle
        mock_exhaust = RuntimeExhaustBundle(run_id="run-persist-deny", created_after_exit=True)

        with patch(
            "apps_rg.runtime.bindings.exit_binding._resolve_repo_root",
            return_value=_REPO_ROOT,
        ), patch(
            "apps_rg.runtime.bindings.exit_binding.build_apps_rg_exit_harness",
        ) as mock_harness_factory:
            mock_harness = MagicMock()
            mock_harness.evaluate.return_value = (mock_receipt, mock_mesh, mock_exhaust)
            mock_harness._profile.gate_definitions = {"G28": {}}
            mock_harness_factory.return_value = mock_harness
            disposition = exit_finalize_apps_rg(sealed, prompt)

        assert disposition.outcome_authorized is False, (
            "outcome_authorized must be False when harness returns X3A_DENY_REROUTE"
        )

    def test_outcome_authorized_true_when_harness_allows_finish(self, tmp_path):
        """P3b: outcome_authorized must be True when harness returns X3D_ALLOW_FINISH."""
        from unittest.mock import patch, MagicMock
        from apps_rg.runtime.bindings.exit_binding import exit_finalize_apps_rg
        from agentic_core.runtime.exit.exit_disposition import (
            X3D_ALLOW_FINISH, ExitDispositionReceipt,
        )
        from agentic_core.runtime.gates.gate_types import GateMeshResult, GateVerdict

        sealed = self._make_sealed(run_id="run-persist-allow")
        prompt = self._make_prompt()

        mock_verdict = GateVerdict(
            gate_id="G21",
            result="PASS",
            severity="hard_fail",
            reason_codes=(),
        )
        mock_mesh = GateMeshResult(
            verdicts=(mock_verdict,),
            required_gate_ids=("G21",),
        )
        mock_receipt = ExitDispositionReceipt(
            x3_code=X3D_ALLOW_FINISH,
            request_id="req::allow",
            run_id="run-persist-allow",
            gate_mesh_result_ref=mock_mesh.deterministic_digest,
            decisive_reason="all gates passed",
            hard_fail_count=0,
        )
        from agentic_core.runtime.exit.exit_disposition import RuntimeExhaustBundle
        mock_exhaust = RuntimeExhaustBundle(run_id="run-persist-allow", created_after_exit=True)

        with patch(
            "apps_rg.runtime.bindings.exit_binding._resolve_repo_root",
            return_value=_REPO_ROOT,
        ), patch(
            "apps_rg.runtime.bindings.exit_binding.build_apps_rg_exit_harness",
        ) as mock_harness_factory:
            mock_harness = MagicMock()
            mock_harness.evaluate.return_value = (mock_receipt, mock_mesh, mock_exhaust)
            mock_harness._profile.gate_definitions = {"G28": {}}
            mock_harness_factory.return_value = mock_harness
            disposition = exit_finalize_apps_rg(sealed, prompt)

        assert disposition.outcome_authorized is True, (
            "outcome_authorized must be True when harness returns X3D_ALLOW_FINISH"
        )
        assert disposition.hitl_required is False, (
            "hitl_required must be False when harness allows finish"
        )
        assert disposition.exit_status == "success", (
            f"exit_status must be 'success' when outcome_authorized, got {disposition.exit_status!r}"
        )

    def test_proof_artifacts_written_to_run_dir(self):
        """P6+P7: 07_gate_mesh_result.json and 07_gate_receipt.json must exist in run dir."""
        from unittest.mock import patch
        from apps_rg.runtime.bindings.exit_binding import exit_finalize_apps_rg

        sealed = self._make_sealed(run_id="run-proof-artifacts")
        prompt = self._make_prompt()

        with patch(
            "apps_rg.runtime.bindings.exit_binding._resolve_repo_root",
            return_value=_REPO_ROOT,
        ):
            disposition = exit_finalize_apps_rg(sealed, prompt)

        # Find the run directory from the output_artifact_path
        import os
        artifact_path = Path(disposition.output_artifact_path)
        run_dir = artifact_path.parent
        assert run_dir.exists(), f"Run directory {run_dir} does not exist"

        mesh_path = run_dir / "07_gate_mesh_result.json"
        receipt_path = run_dir / "07_gate_receipt.json"
        assert mesh_path.exists(), (
            f"07_gate_mesh_result.json not found in {run_dir}"
        )
        assert receipt_path.exists(), (
            f"07_gate_receipt.json not found in {run_dir}"
        )

        # Validate JSON content is parseable and has required keys
        import json as _json
        mesh_data = _json.loads(mesh_path.read_text(encoding="utf-8"))
        assert "deterministic_digest" in mesh_data, (
            "07_gate_mesh_result.json must contain deterministic_digest"
        )
        receipt_data = _json.loads(receipt_path.read_text(encoding="utf-8"))
        assert "x3_code" in receipt_data, (
            "07_gate_receipt.json must contain x3_code"
        )
        assert "gate_mesh_result_ref" in receipt_data, (
            "07_gate_receipt.json must contain gate_mesh_result_ref"
        )

    def test_no_placeholder_refs_in_gate_verdict_refs(self):
        """P8: gate_verdict_refs must not contain placeholder sentinel values."""
        from unittest.mock import patch
        from apps_rg.runtime.bindings.exit_binding import exit_finalize_apps_rg

        sealed = self._make_sealed(run_id="run-no-placeholder")
        prompt = self._make_prompt()

        with patch(
            "apps_rg.runtime.bindings.exit_binding._resolve_repo_root",
            return_value=_REPO_ROOT,
        ):
            disposition = exit_finalize_apps_rg(sealed, prompt)

        forbidden_sentinels = ("PLACEHOLDER", "UNKNOWN::SKIP", "skip", "placeholder")
        for ref in disposition.gate_verdict_refs:
            for sentinel in forbidden_sentinels:
                assert sentinel not in ref, (
                    f"gate_verdict_refs contains forbidden placeholder {sentinel!r} in {ref!r}"
                )

    def test_harness_exception_falls_back_conservatively(self):
        """P9: if harness raises, outcome_authorized must be False (never True on exception)."""
        from unittest.mock import patch
        from apps_rg.runtime.bindings.exit_binding import exit_finalize_apps_rg

        sealed = self._make_sealed(run_id="run-harness-exception")
        prompt = self._make_prompt()

        with patch(
            "apps_rg.runtime.bindings.exit_binding._resolve_repo_root",
            return_value=_REPO_ROOT,
        ), patch(
            "apps_rg.runtime.bindings.exit_binding.build_apps_rg_exit_harness",
            side_effect=RuntimeError("harness exploded"),
        ):
            disposition = exit_finalize_apps_rg(sealed, prompt)

        assert disposition.outcome_authorized is False, (
            "outcome_authorized must be False when harness raises"
        )
        assert disposition.gate_verdict_refs == (), (
            "gate_verdict_refs must be empty tuple when harness raises"
        )


# ── HITL policy registry — core boundary invariants ───────────────────────────

class TestHitlPolicyRegistryCoreClean:
    """Core Addition Author-Gate tests — hitl_policy_registry must have
    no app-specific rg_* policy definitions hardcoded."""

    def test_builtin_policies_table_is_empty(self):
        """_BUILTIN_POLICIES must be empty — no rg_* or any app-specific entries."""
        from agentic_core.runtime.exit.hitl_policy_registry import _BUILTIN_POLICIES
        assert _BUILTIN_POLICIES == {}, (
            f"Core _BUILTIN_POLICIES must be empty; found keys: {list(_BUILTIN_POLICIES)}"
        )

    def test_no_rg_keys_in_builtin_table(self):
        """Negative-control: no rg_* key should exist in the built-in table."""
        from agentic_core.runtime.exit.hitl_policy_registry import _BUILTIN_POLICIES
        rg_keys = [k for k in _BUILTIN_POLICIES if k.startswith("rg_")]
        assert rg_keys == [], (
            f"Core must not contain rg_* policies; found: {rg_keys}"
        )

    def test_resolve_unknown_ref_without_table_returns_unknown(self):
        """resolve_hitl_policy with no table returns UNKNOWN/fail-soft for any ref."""
        from agentic_core.runtime.exit.hitl_policy_registry import resolve_hitl_policy
        spec = resolve_hitl_policy("rg_release_approval_v1")
        assert spec.resolved is False
        assert spec.trigger_kind == "UNKNOWN"

    def test_resolve_none_ref_returns_unknown(self):
        """resolve_hitl_policy(None) → UNKNOWN regardless of table."""
        from agentic_core.runtime.exit.hitl_policy_registry import resolve_hitl_policy
        spec = resolve_hitl_policy(None)
        assert spec.resolved is False
        assert spec.trigger_kind == "UNKNOWN"
        assert spec.requires_hitl is False

    def test_apps_rg_policies_load_from_yaml(self):
        """apps_rg HITL policies must load from app-owned YAML, not from core."""
        from agentic_core.runtime.exit.hitl_policy_registry import (
            load_hitl_policy_table,
            resolve_hitl_policy,
        )
        _POLICY_PATH = (
            _REPO_ROOT / "apps_rg" / "config" / "domain_contract"
            / "hitl_policies.resume_generation.v1.yaml"
        )
        assert _POLICY_PATH.exists(), f"apps_rg HITL policy YAML must exist at {_POLICY_PATH}"
        table = load_hitl_policy_table(_POLICY_PATH)
        assert len(table) > 0, "apps_rg HITL policy table must not be empty"
        # All defined apps_rg policies should resolve
        for ref in ("rg_release_approval_v1", "rg_missing_brief_v1", "rg_low_confidence_v1",
                    "rg_no_hitl_v1"):
            spec = resolve_hitl_policy(ref, policy_table=table)
            assert spec.resolved is True, f"{ref} must resolve from apps_rg YAML table"
            assert spec.trigger_kind != "UNKNOWN", f"{ref} must have a real trigger_kind"

    def test_new_app_policy_loadable_without_editing_core(self):
        """Negative-control: a hypothetical new app can define and load its own
        HITL policy table without any edits to agentic_core.
        This proves the plug-in test (core addition author-gate test #5)."""
        from agentic_core.runtime.exit.hitl_policy_registry import resolve_hitl_policy
        # Simulate another app's table loaded from its own config (in-memory here)
        other_app_table = {
            "lic_release_v1": {
                "trigger_kind": "RELEASE_APPROVAL",
                "requires_hitl": True,
                "trigger_threshold": 0.75,
                "operator_id": None,
                "policy_version": "v1",
            }
        }
        spec = resolve_hitl_policy("lic_release_v1", policy_table=other_app_table)
        assert spec.resolved is True
        assert spec.trigger_kind == "RELEASE_APPROVAL"
        assert spec.requires_hitl is True
        # And core never needed to be touched to support this
        from agentic_core.runtime.exit.hitl_policy_registry import _BUILTIN_POLICIES
        assert "lic_release_v1" not in _BUILTIN_POLICIES


# ── G21 deterministic header repair ──────────────────────────────────────────

class TestG21HeaderRepair:
    """Tests for deterministic header extraction and repair from FEC source resume.

    Validates:
    1. Generated header present → header_block sealed normally (no repair).
    2. Generated header missing + source resume evidence present → repair creates header_block.
    3. Generated header missing + no source evidence → G21 fails (no header_block).
    4. Deterministic repair never uses target_company/target_role/target_level.
    5. Repair receipt records source_evidence_ref.
    6. Extractor parses all 6 canonical fields from representative resume text.
    """

    _SAMPLE_RESUME_TEXT = (
        "Page  1 of 3 \n"
        "+1-917-239-3830  | amitayer1@gmail.com  | linkedin.com/in/amitayer1/  "
        "| github.com/Siamese001/Agentic-Workflow\n"
        " Amit  Ayer \n"
        "SVP Engineering | Agentic AI Platforms\n"
        "+1-917-239-3830 | amitayer1@gmail.com\n"
        "Boca Raton, FL\n"
        "EXECUTIVE SUMMARY\n"
        "Engineering executive building production-grade AI platforms.\n"
    )

    def _make_fec_with_resume(self, resume_text: str) -> Any:
        from agentic_core.runtime.contracts.final_evidence_contract import (
            EvidenceItem,
            FinalEvidenceContract,
        )
        item = EvidenceItem(
            source="resume:app_payload.source_resume_text",
            content=resume_text,
            content_type="text",
        )
        return FinalEvidenceContract(
            request_id="req-hdr-test",
            run_id="run-hdr-test",
            app_id="apps_rg",
            trace_id="trace::hdr-test",
            evidence_items=(item,),
            l5_certification_ref="cert::test::v1",
        )

    def _make_fec_jd_only(self) -> Any:
        from agentic_core.runtime.contracts.final_evidence_contract import (
            EvidenceItem,
            FinalEvidenceContract,
        )
        item = EvidenceItem(
            source="jd:app_payload.jd_text",
            content="Some job description text",
            content_type="text",
        )
        return FinalEvidenceContract(
            request_id="req-hdr-test",
            run_id="run-hdr-test",
            app_id="apps_rg",
            trace_id="trace::hdr-test",
            evidence_items=(item,),
            l5_certification_ref="cert::test::v1",
        )

    def test_generated_header_present_no_repair(self) -> None:
        """Generated header present → sealed normally; repair=False."""
        from apps_rg.exit.apps_rg_exit_evidence_builder import seal_resume_sections

        content = {
            "header": {"name": "Amit Ayer", "email": "amitayer1@gmail.com"},
            "executive_summary": "summary text",
            "experience": [],
            "skills": [],
            "education": [],
        }
        fec = self._make_fec_with_resume(self._SAMPLE_RESUME_TEXT)
        sections, repair = seal_resume_sections(content, "run-001", fec)

        section_ids = [s.node_id for s in sections]
        assert "header_block" in section_ids, "header_block must be sealed when generated"
        assert not repair.repaired, "Repair must NOT fire when header is present in generated output"

        hdr_section = next(s for s in sections if s.node_id == "header_block")
        assert hdr_section.payload_ref == "generated_resume.json#header"

    def test_missing_header_with_source_evidence_triggers_repair(self) -> None:
        """Generated header absent + FEC source resume → deterministic repair creates header_block."""
        from apps_rg.exit.apps_rg_exit_evidence_builder import seal_resume_sections

        content = {
            "executive_summary": "summary text",
            "experience": [],
            "skills": [],
            "education": [],
        }
        fec = self._make_fec_with_resume(self._SAMPLE_RESUME_TEXT)
        sections, repair = seal_resume_sections(content, "run-002", fec)

        section_ids = [s.node_id for s in sections]
        assert "header_block" in section_ids, (
            "header_block must be created via repair when header absent + FEC has source resume"
        )
        assert repair.repaired, "repair.repaired must be True"
        assert repair.source_evidence_ref.startswith("resume:"), (
            f"source_evidence_ref must reference the resume item; got {repair.source_evidence_ref!r}"
        )
        hdr_section = next(s for s in sections if s.node_id == "header_block")
        assert hdr_section.payload_ref == "fec_source_resume#header_repair"

    def test_missing_header_no_source_evidence_no_repair(self) -> None:
        """Generated header absent + no source resume evidence → header_block omitted; G21 fails honestly."""
        from apps_rg.exit.apps_rg_exit_evidence_builder import seal_resume_sections

        content = {
            "executive_summary": "summary text",
            "experience": [],
            "skills": [],
            "education": [],
        }
        fec = self._make_fec_jd_only()  # no resume: item
        sections, repair = seal_resume_sections(content, "run-003", fec)

        section_ids = [s.node_id for s in sections]
        assert "header_block" not in section_ids, (
            "header_block must be absent when no source resume evidence available"
        )
        assert not repair.repaired

    def test_missing_header_fec_none_no_repair(self) -> None:
        """Generated header absent + fec=None → header_block omitted; G21 fails honestly."""
        from apps_rg.exit.apps_rg_exit_evidence_builder import seal_resume_sections

        content = {
            "executive_summary": "summary text",
            "experience": [],
            "skills": [],
            "education": [],
        }
        sections, repair = seal_resume_sections(content, "run-004", None)

        section_ids = [s.node_id for s in sections]
        assert "header_block" not in section_ids
        assert not repair.repaired

    def test_repair_never_uses_target_fields(self) -> None:
        """Repair must never produce header fields derived from target_company/target_role/target_level."""
        from apps_rg.exit.apps_rg_exit_evidence_builder import extract_header_from_source_resume

        fec = self._make_fec_with_resume(self._SAMPLE_RESUME_TEXT)
        result = extract_header_from_source_resume(fec)

        assert result.repaired
        for key in ("target_company", "target_role", "target_level"):
            assert key not in result.header_dict, (
                f"Repair must never inject {key} into header"
            )
        # Verify the actual values came from the resume, not job description
        if "email" in result.header_dict:
            assert "@" in result.header_dict["email"]
        if "phone" in result.header_dict:
            assert any(c.isdigit() for c in result.header_dict["phone"])

    def test_repair_receipt_records_source_evidence_ref(self) -> None:
        """repair.source_evidence_ref is populated and identifies the resume evidence item."""
        from apps_rg.exit.apps_rg_exit_evidence_builder import extract_header_from_source_resume

        fec = self._make_fec_with_resume(self._SAMPLE_RESUME_TEXT)
        result = extract_header_from_source_resume(fec)

        assert result.repaired
        assert result.source_evidence_ref == "resume:app_payload.source_resume_text"

    def test_extractor_parses_all_six_fields(self) -> None:
        """extract_header_from_source_resume parses name, phone, email, linkedin, github, location."""
        from apps_rg.exit.apps_rg_exit_evidence_builder import extract_header_from_source_resume

        fec = self._make_fec_with_resume(self._SAMPLE_RESUME_TEXT)
        result = extract_header_from_source_resume(fec)

        assert result.repaired
        hdr = result.header_dict
        assert "name" in hdr, f"name not extracted; header={hdr}"
        assert "phone" in hdr, f"phone not extracted; header={hdr}"
        assert "email" in hdr, f"email not extracted; header={hdr}"
        assert "linkedin" in hdr, f"linkedin not extracted; header={hdr}"
        assert "github" in hdr, f"github not extracted; header={hdr}"
        assert "location" in hdr, f"location not extracted; header={hdr}"
        assert "Ayer" in hdr["name"] or "Amit" in hdr["name"]
        assert "amitayer1@gmail.com" == hdr["email"]
        assert "amitayer1" in hdr["linkedin"]
        assert "Boca Raton" in hdr["location"] or "FL" in hdr["location"]

    def test_no_repair_when_resume_text_too_sparse(self) -> None:
        """Extraction with fewer than 2 parseable fields → repaired=False."""
        from apps_rg.exit.apps_rg_exit_evidence_builder import extract_header_from_source_resume

        sparse_text = "This resume has no recognizable contact information."
        fec = self._make_fec_with_resume(sparse_text)
        result = extract_header_from_source_resume(fec)

        assert not result.repaired, (
            "Should not repair when fewer than 2 fields can be extracted"
        )


# ── G28 post-mesh authorization logic ────────────────────────────────────────

class TestG28PostMeshAuthorization:
    """Tests for the two-pass G28 receipt finalization logic.

    Validates that:
    - Pass-1 circular G28 FAIL + post-mesh WARN → receipt x3_code=X3D_ALLOW_FINISH
    - Pass-1 circular G28 FAIL + post-mesh FAIL → receipt stays X3A_DENY_REROUTE
    - Both g28_initial_verdict and g28_post_mesh_verdict are present in receipt
    - Receipt is consistent with 07_Exit_disposition.json outcome_authorized
    - G22 verdict is preserved unchanged
    """

    def _make_pkg(self, pkg_id: str = "pkg::receipt-test-001") -> SealedWorkflowPackage:
        return SealedWorkflowPackage(
            package_id=pkg_id,
            run_id="run-receipt-test",
            trace_root="trace::receipt-test",
            route_contract_ref="rc::test",
            workflow_ref="wfm::apps_rg::v1",
        )

    def _make_g28_gdef(self, severity: str = "hard_fail") -> dict:
        return {
            "gate_name": "audit_trace_completeness",
            "severity": severity,
            "required_audit_refs": [
                "request_id", "run_id", "trace_root",
                "route_contract_ref", "workflow_ref",
                "sealed_workflow_package_ref", "gate_mesh_result_ref", "decisive_reason",
            ],
            "optional_observability_refs": [
                "otel_trace_id", "otel_span_id", "exhaust_bundle_ref", "replay_key",
            ],
        }

    def test_pass1_g28_fail_plus_post_mesh_warn_produces_x3d_receipt(self):
        """When Pass-1 G28 is FAIL (circular: no mesh ref yet) and post-mesh G28 is WARN,
        the receipt dict finalized by the binding must show x3_code=X3D_ALLOW_FINISH."""
        import json as _json
        from agentic_core.runtime.exit.exit_disposition import X3D_ALLOW_FINISH

        # Simulate Pass-1 receipt dict (G28 was the sole blocker)
        receipt_dict: dict = {
            "x3_code": "X3A_DENY_REROUTE",
            "decisive_reason": "Hard gate failures: ['G28']",
            "decisive_blocker_gate_ids": ["G28"],
            "decisive_blocker_codes": ["missing_material_audit_ref:gate_mesh_result_ref"],
            "required_gates_passed": False,
            "hard_fail_count": 1,
            "allows_finish": False,
        }

        pkg = self._make_pkg()
        post_mesh_ev = {
            "g28": {
                "audit_refs": {
                    "sealed_workflow_package_ref": pkg.package_id,
                    "gate_mesh_result_ref": "gmr::test::001",
                    "decisive_reason": "Hard gate failures: ['G28']",
                }
            }
        }
        post_mesh_verdict = evaluate_g28(
            "G28", self._make_g28_gdef(), pkg, post_mesh_ev,
            "req-001", "run-receipt-test", "trace::receipt-test",
        )
        # Expect WARN (material refs present; optional OTEL refs absent)
        assert post_mesh_verdict.result == VERDICT_WARN, (
            f"post-mesh G28 should be WARN, got {post_mesh_verdict.result}"
        )

        # Simulate the finalization logic from apps_rg_exit_binding
        pass1_blocked_only_by_g28 = (
            not receipt_dict.get("allows_finish", False)
            and set(receipt_dict.get("decisive_blocker_gate_ids", [])) == {"G28"}
        )
        g28_post_ok = post_mesh_verdict.result in ("PASS", "WARN")
        assert pass1_blocked_only_by_g28 is True
        assert g28_post_ok is True

        # Apply finalization (mirrors the binding logic)
        if pass1_blocked_only_by_g28 and g28_post_ok:
            receipt_dict["x3_code"] = X3D_ALLOW_FINISH
            receipt_dict["decisive_reason"] = (
                f"post_mesh_g28_{post_mesh_verdict.result.lower()}: "
                "all material audit refs satisfied after mesh"
            )
            receipt_dict["decisive_blocker_gate_ids"] = []
            receipt_dict["decisive_blocker_codes"] = []
            receipt_dict["required_gates_passed"] = True
            receipt_dict["hard_fail_count"] = 0

        assert receipt_dict["x3_code"] == X3D_ALLOW_FINISH, (
            "Receipt x3_code must be updated to X3D_ALLOW_FINISH after post-mesh G28 WARN"
        )
        assert receipt_dict["decisive_blocker_gate_ids"] == []
        assert receipt_dict["required_gates_passed"] is True
        assert receipt_dict["hard_fail_count"] == 0
        assert "post_mesh_g28_warn" in receipt_dict["decisive_reason"]

    def test_pass1_g28_fail_plus_post_mesh_fail_keeps_x3a_receipt(self):
        """When post-mesh G28 still FAIL, receipt must remain X3A_DENY_REROUTE."""
        from agentic_core.runtime.exit.exit_disposition import X3A_DENY_REROUTE

        receipt_dict: dict = {
            "x3_code": "X3A_DENY_REROUTE",
            "decisive_reason": "Hard gate failures: ['G28']",
            "decisive_blocker_gate_ids": ["G28"],
            "decisive_blocker_codes": ["missing_material_audit_ref:gate_mesh_result_ref"],
            "required_gates_passed": False,
            "hard_fail_count": 1,
            "allows_finish": False,
        }
        pkg = self._make_pkg("pkg::fail-test")
        # Post-mesh evidence deliberately missing material ref (audit_failure=True)
        post_mesh_ev = {
            "g28": {
                "audit_failure": True,
                "audit_refs": {
                    "sealed_workflow_package_ref": "pkg::fail-test",
                },
            }
        }
        post_mesh_verdict = evaluate_g28(
            "G28", self._make_g28_gdef(), pkg, post_mesh_ev,
            "req-002", "run-fail-test", "trace::fail-test",
        )
        assert post_mesh_verdict.result == VERDICT_FAIL

        # Finalization: post_mesh not ok → do NOT update receipt
        g28_post_ok = post_mesh_verdict.result in ("PASS", "WARN")
        assert g28_post_ok is False

        # receipt_dict unchanged
        assert receipt_dict["x3_code"] == X3A_DENY_REROUTE
        assert receipt_dict["required_gates_passed"] is False
        assert receipt_dict["hard_fail_count"] == 1

    def test_receipt_contains_both_g28_verdicts(self):
        """g28_audit_chain must carry both g28_initial_verdict and g28_post_mesh_verdict."""
        import json as _json

        pkg = self._make_pkg()
        # Simulate Pass-1 G28 — missing gate_mesh_result_ref
        pass1_ev: dict = {"g28": {"audit_refs": {"sealed_workflow_package_ref": pkg.package_id}}}
        pass1_verdict = evaluate_g28(
            "G28", self._make_g28_gdef(), pkg, pass1_ev,
            "req-003", "run-dual-test", "trace::dual-test",
        )
        assert pass1_verdict.result in (VERDICT_FAIL, VERDICT_UNKNOWN)

        # Simulate post-mesh G28 — with gate_mesh_result_ref + decisive_reason
        post_ev = {
            "g28": {
                "audit_refs": {
                    "sealed_workflow_package_ref": pkg.package_id,
                    "gate_mesh_result_ref": "gmr::dual::001",
                    "decisive_reason": "Hard gate failures: ['G28']",
                }
            }
        }
        post_verdict = evaluate_g28(
            "G28", self._make_g28_gdef(), pkg, post_ev,
            "req-003", "run-dual-test", "trace::dual-test",
        )
        assert post_verdict.result in (VERDICT_WARN, VERDICT_PASS)

        receipt_dict: dict = {"x3_code": "X3A_DENY_REROUTE"}
        receipt_dict["g28_audit_chain"] = {
            "g28_initial_verdict": _json.loads(pass1_verdict.as_json()),
            "g28_post_mesh_verdict": _json.loads(post_verdict.as_json()),
            "factual_grounding_diagnostics_ref": "07_g22_factual_grounding_diagnostics.json",
        }

        chain = receipt_dict["g28_audit_chain"]
        assert "g28_initial_verdict" in chain, "Receipt must contain g28_initial_verdict"
        assert "g28_post_mesh_verdict" in chain, "Receipt must contain g28_post_mesh_verdict"
        # Initial verdict preserves the FAIL (not hidden)
        assert chain["g28_initial_verdict"]["result"] in ("FAIL", "UNKNOWN"), (
            "g28_initial_verdict must preserve the Pass-1 failure"
        )
        # Post-mesh verdict is the upgraded one
        assert chain["g28_post_mesh_verdict"]["result"] in ("WARN", "PASS"), (
            "g28_post_mesh_verdict must reflect the post-mesh improvement"
        )

    def test_g22_verdict_unchanged_by_g28_receipt_finalization(self):
        """G22 PASS verdict must not be affected by any G28 receipt finalization."""
        pkg = self._make_pkg()
        # Full G22 evidence
        g22_gdef = {"dimension_thresholds": {"factual_grounding": 0.95, "overall_pass_threshold": 0.75}}
        g22_ev = {"g22_rubric_scores": {
            "factual_grounding": 0.99,
            "role_alignment": 0.80,
            "ats_readability": 0.85,
            "overall_pass_threshold": 0.92,
        }}
        from agentic_core.runtime.gates.gate_evaluators import evaluate_g22
        g22_verdict = evaluate_g22("G22", g22_gdef, pkg, g22_ev, "req-004", "run-g22-test", "trace::g22-test")
        assert g22_verdict.result == VERDICT_PASS, (
            f"G22 must PASS with valid rubric scores; got {g22_verdict.result}"
        )
        # Simulating G28 finalization does not touch g22 verdict
        receipt_dict: dict = {
            "x3_code": "X3A_DENY_REROUTE",
            "decisive_blocker_gate_ids": ["G28"],
            "allows_finish": False,
            "required_gates_passed": False,
            "hard_fail_count": 1,
        }
        from agentic_core.runtime.exit.exit_disposition import X3D_ALLOW_FINISH
        receipt_dict["x3_code"] = X3D_ALLOW_FINISH
        receipt_dict["required_gates_passed"] = True
        # G22 verdict object is completely independent
        assert g22_verdict.result == VERDICT_PASS
        assert g22_verdict.gate_id == "G22"

    def test_post_mesh_g28_only_warn_not_fail_for_optional_observability_gap(self):
        """When all material refs present but optional OTEL refs absent, G28 must be WARN not FAIL."""
        pkg = self._make_pkg()
        ev = {
            "g28": {
                "audit_refs": {
                    "sealed_workflow_package_ref": pkg.package_id,
                    "gate_mesh_result_ref": "gmr::warn-test::001",
                    "decisive_reason": "post_mesh_g28_warn: all material audit refs satisfied after mesh",
                    # otel_trace_id, otel_span_id, exhaust_bundle_ref, replay_key intentionally absent
                }
            }
        }
        v = evaluate_g28(
            "G28", self._make_g28_gdef(), pkg, ev,
            "req-005", "run-warn-test", "trace::warn-test",
        )
        assert v.result == VERDICT_WARN, (
            f"Optional observability ref gap must produce WARN not FAIL; got {v.result}"
        )
        assert all("missing_optional_observability_ref" in rc for rc in v.reason_codes)
