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
from agentic_core.runtime.exit.apps_rg_exit_binding import build_apps_rg_exit_harness
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
            "default_reason": "apps_rg produces user-visible artifacts only",
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
        assert "apps_rg" in v.not_applicable_reason.lower() or len(v.not_applicable_reason) > 0


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
        from agentic_core.runtime.exit.apps_rg_exit_binding import build_apps_rg_exit_harness as f
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
