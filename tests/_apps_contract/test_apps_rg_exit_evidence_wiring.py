"""Tests for apps_rg exit evidence wiring — G22, G24, G28 helpers.

Covers:
  A. compute_g22_rubric_scores — unit tests for each scored dim (apps_rg-owned)
  B. build_g24_provenance — all required fields populated from real hashes (apps_rg-owned)
  C. evaluate_g22 passes when correct scores present in evidence
  D. evaluate_g24 passes when g24_provenance covers all required fields
  E. exit_finalize_apps_rg passes evidence dict to harness.evaluate()
  F. Architecture invariants — no per_input_hash_map on generic contract;
     component_hash_map carries per-input hashes; builders live in apps_rg/

Plan: apps-rg-exit-gate-wiring / architecture-cleanup
"""
from __future__ import annotations

import hashlib as _hashlib
import json
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.runtime.contracts.compiled_prompt_artifact import (
    CompiledPromptArtifact,
)
from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
from agentic_core.runtime.contracts.sealed_workflow_types import (
    SealedWorkflowPackage,
)
from apps_rg.exit.apps_rg_exit_evidence_builder import (
    FactualGroundingResult,
    MissingPerInputHashError,
    build_g24_provenance as _build_g24_provenance,
    compute_factual_grounding as _compute_factual_grounding,
    compute_g22_rubric_scores as _compute_deterministic_dim_scores,
)
from agentic_core.runtime.gates.gate_evaluators import evaluate_g22, evaluate_g24


# ── Fixtures ──────────────────────────────────────────────────────────────────

_L5_CERT_REF = "exit-apps-rg-resume-generation-w3p5"


def _make_sealed(
    *,
    generated_content: str = "",
    compilation_hash: str = "sha256::abc123",
    prompt_artifact_digest: str = "sha256::def456",
    run_id: str = "run-test-001",
    trace_id: str = "trace-test-001",
    request_id: str = "req-test-001",
    tenant_id: str = "apps_rg",
) -> SealedL2Artifact:
    return SealedL2Artifact(
        generated_content=generated_content,
        compilation_hash=compilation_hash,
        prompt_artifact_digest=prompt_artifact_digest,
        run_id=run_id,
        trace_id=trace_id,
        request_id=request_id,
        tenant_id=tenant_id,
        app_id="apps_rg",
        execution_status="completed",
        l5_certification_ref=_L5_CERT_REF,
    )


def _make_prompt(
    *,
    compilation_hash: str = "sha256::prompt-comp-hash",
    evidence_digest: str = "sha256::evidence-digest",
    component_hash_map: dict | None = None,
) -> CompiledPromptArtifact:
    return CompiledPromptArtifact(
        request_id="req-test-001",
        run_id="run-test-001",
        app_id="apps_rg",
        trace_id="trace-test-001",
        compilation_hash=compilation_hash,
        evidence_digest=evidence_digest,
        target_model="Qwen/Qwen2.5-32B-Instruct-AWQ",
        target_provider="vllm",
        l5_certification_ref=_L5_CERT_REF,
        component_hash_map=component_hash_map or {},
    )


def _make_pkg(
    *,
    package_id: str = "pkg::apps_rg::run-test-001",
    run_id: str = "run-test-001",
    trace_root: str = "trace-test-001",
    route_contract_ref: str = "rcr::apps_rg::resume_generation::v1",
    workflow_ref: str = "wfm::apps_rg::resume_generation::v1",
    workflow_manifest_ref: str = "wfm::apps_rg::resume_generation::v1",
    merged_content_digest: str = "sha256::abc123",
    merged_payload_digest: str = "sha256::abc123",
    replay_manifest: str = "sha256::abc123",
) -> SealedWorkflowPackage:
    return SealedWorkflowPackage(
        package_id=package_id,
        run_id=run_id,
        trace_root=trace_root,
        route_contract_ref=route_contract_ref,
        workflow_ref=workflow_ref,
        workflow_manifest_ref=workflow_manifest_ref,
        merged_content_digest=merged_content_digest,
        merged_payload_digest=merged_payload_digest,
        replay_manifest=replay_manifest,
    )


# ── F. Architecture invariants ───────────────────────────────────────────────

class TestArchitectureInvariants:
    """F. Verify generic core contract has no apps_rg-specific field; per-input
    hashes travel via component_hash_map; builders live in apps_rg/."""

    def test_compiled_prompt_artifact_has_no_per_input_hash_map_field(self):
        """per_input_hash_map must NOT exist as a field on the generic contract."""
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(CompiledPromptArtifact)}
        assert "per_input_hash_map" not in field_names, (
            "per_input_hash_map is apps_rg-specific and must not appear on the "
            "generic CompiledPromptArtifact contract"
        )

    def test_component_hash_map_carries_per_input_hashes_for_apps_rg(self):
        """apps_rg PA binding deposits jd_hash/resume_hash/target_role_spec_hash
        into component_hash_map (the generic field), not into a new field."""
        chm = {
            "jd_hash": _sha256("jd text"),
            "resume_hash": _sha256("resume text"),
            "target_role_spec_hash": _sha256("co|role|level"),
        }
        prompt = _make_prompt(component_hash_map=chm)
        # component_hash_map exists and carries the expected keys
        assert "jd_hash" in prompt.component_hash_map
        assert "resume_hash" in prompt.component_hash_map
        assert "target_role_spec_hash" in prompt.component_hash_map

    def test_g22_builder_is_importable_from_apps_rg(self):
        """compute_g22_rubric_scores lives in apps_rg.exit, not in agentic_core."""
        from apps_rg.exit.apps_rg_exit_evidence_builder import compute_g22_rubric_scores
        assert callable(compute_g22_rubric_scores)

    def test_g24_builder_is_importable_from_apps_rg(self):
        """build_g24_provenance lives in apps_rg.exit, not in agentic_core."""
        from apps_rg.exit.apps_rg_exit_evidence_builder import build_g24_provenance
        assert callable(build_g24_provenance)

    def test_core_exit_binding_does_not_define_g22_scorer(self):
        """_compute_deterministic_dim_scores must not be defined in agentic_core."""
        import inspect
        import agentic_core.runtime.exit.apps_rg_exit_binding as _mod
        fn = getattr(_mod, "_compute_deterministic_dim_scores", None)
        if fn is not None:
            src_file = inspect.getfile(fn)
            assert "apps_rg" in src_file and "agentic_core" not in src_file, (
                "_compute_deterministic_dim_scores must be defined in apps_rg/, "
                f"not in {src_file}"
            )

    def test_core_exit_binding_does_not_define_g24_provenance_builder(self):
        """_build_g24_provenance must not be defined in agentic_core."""
        import inspect
        import agentic_core.runtime.exit.apps_rg_exit_binding as _mod
        fn = getattr(_mod, "_build_g24_provenance", None)
        if fn is not None:
            src_file = inspect.getfile(fn)
            assert "apps_rg" in src_file and "agentic_core" not in src_file, (
                "_build_g24_provenance must be defined in apps_rg/, "
                f"not in {src_file}"
            )

    def test_missing_per_input_hashes_raises_not_fallback(self):
        """When component_hash_map has no per-input keys, build_g24_provenance
        must raise MissingPerInputHashError — NOT silently substitute evidence_digest."""
        prompt = _make_prompt(
            evidence_digest="sha256::fec-aggregate",
            component_hash_map={},  # no per-input keys
        )
        with pytest.raises(MissingPerInputHashError) as exc_info:
            _build_g24_provenance(_make_sealed(), prompt, _make_pkg())
        assert "jd_hash" in exc_info.value.missing_keys
        assert "resume_hash" in exc_info.value.missing_keys
        assert "target_role_spec_hash" in exc_info.value.missing_keys

    def test_evidence_digest_not_used_as_jd_hash_substitute(self):
        """evidence_digest must never appear as jd_hash — it is an aggregate."""
        fec = "sha256::fec-aggregate-value"
        prompt = _make_prompt(
            evidence_digest=fec,
            component_hash_map={},
        )
        with pytest.raises(MissingPerInputHashError):
            prov = _build_g24_provenance(_make_sealed(), prompt, _make_pkg())
            assert prov.get("jd_hash") != fec, (
                "evidence_digest must not substitute for jd_hash"
            )

    def test_evidence_digest_not_used_as_resume_hash_substitute(self):
        """evidence_digest must never appear as resume_candidate_profile_hash."""
        fec = "sha256::fec-aggregate-value"
        prompt = _make_prompt(
            evidence_digest=fec,
            component_hash_map={},
        )
        with pytest.raises(MissingPerInputHashError):
            prov = _build_g24_provenance(_make_sealed(), prompt, _make_pkg())
            assert prov.get("resume_candidate_profile_hash") != fec, (
                "evidence_digest must not substitute for resume_candidate_profile_hash"
            )


# ── A. compute_g22_rubric_scores (apps_rg-owned) ──────────────────────────────

class TestComputeDeterministicDimScores:
    """A. Unit tests for the deterministic dimension scorer (apps_rg-owned)."""

    def test_empty_parsed_content_returns_empty(self):
        sealed = _make_sealed()
        result = _compute_deterministic_dim_scores(None, sealed)
        assert result == {}

    def test_format_compliance_all_keys_present(self):
        content = {
            "executive_summary": "SVP Engineering with 15 years...",
            "experience": [{"company": "Acme", "title": "SVP"}],
            "education": [{"degree": "BS CS"}],
            "skills": ["Python", "AWS"],
        }
        sealed = _make_sealed()
        scores = _compute_deterministic_dim_scores(content, sealed)
        assert scores["format_compliance"] == 1.0

    def test_format_compliance_partial_keys(self):
        content = {"executive_summary": "Summary here", "experience": []}
        sealed = _make_sealed()
        scores = _compute_deterministic_dim_scores(content, sealed)
        assert scores["format_compliance"] == 0.5  # 2 of 4 keys

    def test_ats_readability_clean_ascii_scores_high(self):
        content = {
            "executive_summary": "Clean ASCII resume content.",
            "experience": [],
            "education": [],
            "skills": [],
        }
        sealed = _make_sealed()
        scores = _compute_deterministic_dim_scores(content, sealed)
        assert scores["ats_readability"] >= 0.99

    def test_no_fabrication_clean_content(self):
        content = {"executive_summary": "Genuine resume content."}
        sealed = _make_sealed()
        scores = _compute_deterministic_dim_scores(content, sealed)
        assert scores["no_fabrication"] == 1.0

    def test_no_fabrication_flagged_on_marker(self):
        content = {"executive_summary": "FABRICATED content for test."}
        sealed = _make_sealed()
        scores = _compute_deterministic_dim_scores(content, sealed)
        assert scores["no_fabrication"] == 0.0

    def test_factual_grounding_absent_from_deterministic_scores(self):
        """factual_grounding requires upstream evidence; deterministic scorer leaves it absent."""
        sealed = _make_sealed()
        content = {"executive_summary": "Content."}
        scores = _compute_deterministic_dim_scores(content, sealed)
        assert "factual_grounding" not in scores

    def test_concision_normal_word_count(self):
        content = {"executive_summary": " ".join(["word"] * 500)}
        sealed = _make_sealed()
        scores = _compute_deterministic_dim_scores(content, sealed)
        assert scores["concision"] == 1.0

    def test_concision_penalised_on_very_long_content(self):
        content = {"executive_summary": " ".join(["word"] * 2000)}
        sealed = _make_sealed()
        scores = _compute_deterministic_dim_scores(content, sealed)
        assert scores["concision"] < 1.0

    def test_overall_pass_threshold_present(self):
        content = {
            "executive_summary": "Good content.",
            "experience": [],
            "education": [],
            "skills": [],
        }
        sealed = _make_sealed()
        scores = _compute_deterministic_dim_scores(content, sealed)
        assert "overall_pass_threshold" in scores
        assert 0.0 <= scores["overall_pass_threshold"] <= 1.0


# ── B. build_g24_provenance (apps_rg-owned) ──────────────────────────────────


def _sha256(text: str) -> str:
    return _hashlib.sha256(text.encode("utf-8")).hexdigest()


class TestBuildG24Provenance:
    """B. G24 provenance uses real per-input hashes; jd_hash != resume_hash when inputs differ."""

    # ── per-input hash lineage ────────────────────────────────────────────────

    def test_jd_hash_comes_from_component_hash_map(self):
        """jd_hash is derived from JD content only, deposited in component_hash_map."""
        jd_h = _sha256("job description text only")
        resume_h = _sha256("source resume text only")
        prompt = _make_prompt(
            component_hash_map={"jd_hash": jd_h, "resume_hash": resume_h,
                                 "target_role_spec_hash": _sha256("co|role|level")},
        )
        prov = _build_g24_provenance(_make_sealed(), prompt, _make_pkg())
        assert prov["jd_hash"] == jd_h

    def test_resume_candidate_profile_hash_comes_from_component_hash_map(self):
        """resume_candidate_profile_hash is derived from resume content only."""
        jd_h = _sha256("job description text only")
        resume_h = _sha256("source resume text only")
        prompt = _make_prompt(
            component_hash_map={"jd_hash": jd_h, "resume_hash": resume_h,
                                 "target_role_spec_hash": _sha256("co|role|level")},
        )
        prov = _build_g24_provenance(_make_sealed(), prompt, _make_pkg())
        assert prov["resume_candidate_profile_hash"] == resume_h

    def test_jd_hash_ne_resume_hash_when_inputs_differ(self):
        """Core anti-aliasing invariant: jd_hash != resume_candidate_profile_hash when inputs differ."""
        jd_h = _sha256("job description for SVP IT Strategy role at Brown & Brown")
        resume_h = _sha256("Amit Ayer SVP Engineering resume with 15 years experience")
        assert jd_h != resume_h, "Test data inputs must actually differ"
        prompt = _make_prompt(
            component_hash_map={"jd_hash": jd_h, "resume_hash": resume_h,
                                 "target_role_spec_hash": _sha256("brown|svp it strategy|executive")},
        )
        prov = _build_g24_provenance(_make_sealed(), prompt, _make_pkg())
        assert prov["jd_hash"] != prov["resume_candidate_profile_hash"], (
            "jd_hash and resume_candidate_profile_hash must not alias to the same digest "
            "when JD and resume are different inputs"
        )

    def test_target_role_spec_hash_distinct_from_jd_and_resume(self):
        """target_role_spec_hash is SHA-256('company|role|level'), distinct from JD and resume hashes."""
        jd_h = _sha256("detailed job description text")
        resume_h = _sha256("detailed resume text")
        role_h = _sha256("brown & brown|svp it strategy & innovation|EXECUTIVE")
        prompt = _make_prompt(
            component_hash_map={"jd_hash": jd_h, "resume_hash": resume_h,
                                 "target_role_spec_hash": role_h},
        )
        prov = _build_g24_provenance(_make_sealed(), prompt, _make_pkg())
        assert prov["target_role_spec_hash"] == role_h
        assert prov["target_role_spec_hash"] != prov["jd_hash"]
        assert prov["target_role_spec_hash"] != prov["resume_candidate_profile_hash"]

    # ── aggregate_evidence_hash is present but does not substitute ────────────

    def test_aggregate_evidence_hash_present_and_not_substitute(self):
        """aggregate_evidence_hash exists alongside per-input fields but is not equal to them."""
        jd_h = _sha256("jd text")
        resume_h = _sha256("resume text")
        fec_agg = _sha256("fec_compilation_hash_aggregate_over_all_evidence")
        assert jd_h != fec_agg and resume_h != fec_agg, "Test data must produce distinct hashes"
        prompt = _make_prompt(
            evidence_digest=fec_agg,
            component_hash_map={"jd_hash": jd_h, "resume_hash": resume_h,
                                 "target_role_spec_hash": _sha256("co|role|level")},
        )
        prov = _build_g24_provenance(_make_sealed(), prompt, _make_pkg())
        assert "aggregate_evidence_hash" in prov
        assert prov["aggregate_evidence_hash"] == fec_agg
        assert prov["jd_hash"] != prov["aggregate_evidence_hash"]
        assert prov["resume_candidate_profile_hash"] != prov["aggregate_evidence_hash"]

    # ── missing per-input hash → raises, never falls back ───────────────────

    def test_missing_jd_hash_raises(self):
        """Missing jd_hash in component_hash_map raises MissingPerInputHashError."""
        prompt = _make_prompt(
            component_hash_map={
                "resume_hash": _sha256("resume"),
                "target_role_spec_hash": _sha256("co|role|level"),
                # jd_hash absent
            }
        )
        with pytest.raises(MissingPerInputHashError) as exc_info:
            _build_g24_provenance(_make_sealed(), prompt, _make_pkg())
        assert "jd_hash" in exc_info.value.missing_keys

    def test_missing_resume_hash_raises(self):
        """Missing resume_hash in component_hash_map raises MissingPerInputHashError."""
        prompt = _make_prompt(
            component_hash_map={
                "jd_hash": _sha256("jd"),
                "target_role_spec_hash": _sha256("co|role|level"),
                # resume_hash absent
            }
        )
        with pytest.raises(MissingPerInputHashError) as exc_info:
            _build_g24_provenance(_make_sealed(), prompt, _make_pkg())
        assert "resume_hash" in exc_info.value.missing_keys

    def test_missing_target_role_spec_hash_raises(self):
        """Missing target_role_spec_hash in component_hash_map raises MissingPerInputHashError."""
        prompt = _make_prompt(
            component_hash_map={
                "jd_hash": _sha256("jd"),
                "resume_hash": _sha256("resume"),
                # target_role_spec_hash absent
            }
        )
        with pytest.raises(MissingPerInputHashError) as exc_info:
            _build_g24_provenance(_make_sealed(), prompt, _make_pkg())
        assert "target_role_spec_hash" in exc_info.value.missing_keys

    def test_empty_component_hash_map_raises_all_three(self):
        """Empty component_hash_map reports all three missing keys."""
        prompt = _make_prompt(evidence_digest="sha256::fec-agg", component_hash_map={})
        with pytest.raises(MissingPerInputHashError) as exc_info:
            _build_g24_provenance(_make_sealed(), prompt, _make_pkg())
        missing = exc_info.value.missing_keys
        assert set(missing) == {"jd_hash", "resume_hash", "target_role_spec_hash"}

    def test_aggregate_evidence_hash_is_still_set_when_hashes_present(self):
        """aggregate_evidence_hash is set from evidence_digest when all per-input hashes present."""
        fec = "sha256::fec-agg-value"
        prompt = _make_prompt(
            evidence_digest=fec,
            component_hash_map={
                "jd_hash": _sha256("jd"),
                "resume_hash": _sha256("resume"),
                "target_role_spec_hash": _sha256("co|role|level"),
            },
        )
        prov = _build_g24_provenance(_make_sealed(), prompt, _make_pkg())
        assert prov["aggregate_evidence_hash"] == fec

    # ── structural checks ─────────────────────────────────────────────────────

    def test_replay_key_uses_sealed_compilation_hash(self):
        sealed = _make_sealed(compilation_hash="sha256::output-hash")
        prompt = _make_prompt(component_hash_map={
            "jd_hash": _sha256("jd"),
            "resume_hash": _sha256("resume"),
            "target_role_spec_hash": _sha256("co|role|level"),
        })
        prov = _build_g24_provenance(sealed, prompt, _make_pkg())
        assert prov["replay_key"] == "sha256::output-hash"

    def test_output_artifact_digest_populated(self):
        sealed = _make_sealed(compilation_hash="sha256::output-hash")
        prompt = _make_prompt(component_hash_map={
            "jd_hash": _sha256("jd"),
            "resume_hash": _sha256("resume"),
            "target_role_spec_hash": _sha256("co|role|level"),
        })
        prov = _build_g24_provenance(sealed, prompt,
                                      _make_pkg(merged_content_digest="sha256::output-hash"))
        assert prov["output_artifact_digest"] == "sha256::output-hash"

    def test_all_ref_fields_present(self):
        prompt = _make_prompt(component_hash_map={
            "jd_hash": _sha256("jd"),
            "resume_hash": _sha256("resume"),
            "target_role_spec_hash": _sha256("co|role|level"),
        })
        prov = _build_g24_provenance(_make_sealed(), prompt, _make_pkg())
        for f in ["output_schema_ref", "rubric_ref", "threshold_profile_ref",
                  "grader_roster_ref", "workflow_manifest_ref",
                  "sealed_workflow_artifact_ref", "prompt_profile_ref"]:
            assert f in prov and prov[f], f"Missing/empty ref field: {f}"

    def test_no_empty_hash_fields(self):
        """All hash fields must be non-empty when real data is provided."""
        jd_h = _sha256("jd")
        resume_h = _sha256("resume")
        role_h = _sha256("co|role|level")
        prompt = _make_prompt(
            evidence_digest="sha256::real-fec",
            compilation_hash="sha256::real-prompt",
            component_hash_map={"jd_hash": jd_h, "resume_hash": resume_h,
                                 "target_role_spec_hash": role_h},
        )
        prov = _build_g24_provenance(_make_sealed(compilation_hash="sha256::real"), prompt, _make_pkg())
        for f in ["replay_key", "resume_candidate_profile_hash", "jd_hash", "target_role_spec_hash"]:
            assert prov[f], f"Hash field '{f}' must not be empty"


# ── C. evaluate_g22 with evidence scores ─────────────────────────────────────

class TestEvaluateG22WithEvidence:
    """C. evaluate_g22 returns PASS when required dim scores meet thresholds."""

    def _gate_def(self) -> dict:
        return {
            "gate_id": "G22",
            "severity": "hard",
            "dimension_thresholds": {
                "format_compliance": 0.80,
                "ats_readability": 0.80,
                "no_fabrication": 0.90,
            },
        }

    def test_pass_when_all_dims_above_threshold(self):
        from agentic_core.runtime.gates.gate_evaluators import VERDICT_PASS
        pkg = _make_pkg()
        evidence = {
            "g22_rubric_scores": {
                "format_compliance": 1.0,
                "ats_readability": 0.99,
                "no_fabrication": 1.0,
                "overall_pass_threshold": 0.99,
            }
        }
        verdict = evaluate_g22("G22", self._gate_def(), pkg, evidence, "req-1", "run-1", "trace-1")
        assert verdict.result == VERDICT_PASS

    def test_fail_when_dim_below_threshold(self):
        from agentic_core.runtime.gates.gate_evaluators import VERDICT_FAIL
        pkg = _make_pkg()
        evidence = {
            "g22_rubric_scores": {
                "format_compliance": 0.50,  # below 0.80 threshold
                "ats_readability": 0.99,
                "no_fabrication": 1.0,
            }
        }
        verdict = evaluate_g22("G22", self._gate_def(), pkg, evidence, "req-1", "run-1", "trace-1")
        assert verdict.result == VERDICT_FAIL

    def test_unknown_when_no_scores(self):
        from agentic_core.runtime.gates.gate_evaluators import VERDICT_UNKNOWN
        pkg = _make_pkg()
        evidence = {"g22_rubric_scores": {}}
        verdict = evaluate_g22("G22", self._gate_def(), pkg, evidence, "req-1", "run-1", "trace-1")
        assert verdict.result == VERDICT_UNKNOWN

    def test_unknown_when_required_dim_missing(self):
        from agentic_core.runtime.gates.gate_evaluators import VERDICT_UNKNOWN
        pkg = _make_pkg()
        evidence = {
            "g22_rubric_scores": {
                "format_compliance": 1.0,
                # ats_readability missing
                "no_fabrication": 1.0,
            }
        }
        verdict = evaluate_g22("G22", self._gate_def(), pkg, evidence, "req-1", "run-1", "trace-1")
        assert verdict.result == VERDICT_UNKNOWN


# ── D. evaluate_g24 with provenance evidence ─────────────────────────────────

class TestEvaluateG24WithEvidence:
    """D. evaluate_g24 returns PASS when g24_provenance covers required fields."""

    def _gate_def(self) -> dict:
        return {
            "gate_id": "G24",
            "severity": "hard",
            "required_provenance_fields": [
                "request_id",
                "run_id",
                "trace_root",
                "replay_key",
                "resume_candidate_profile_hash",
                "jd_hash",
                "target_role_spec_hash",
                "output_schema_ref",
                "rubric_ref",
                "threshold_profile_ref",
                "grader_roster_ref",
                "workflow_manifest_ref",
                "sealed_section_artifact_refs",
                "sealed_workflow_artifact_ref",
                "output_artifact_digest",
            ],
        }

    def test_pass_when_all_fields_populated(self):
        from agentic_core.runtime.gates.gate_evaluators import VERDICT_PASS
        sealed = _make_sealed(compilation_hash="sha256::out")
        prompt = _make_prompt(
            evidence_digest="sha256::fec",
            compilation_hash="sha256::prompt",
            component_hash_map={
                "jd_hash": _sha256("jd"),
                "resume_hash": _sha256("resume"),
                "target_role_spec_hash": _sha256("co|role|level"),
            },
        )
        pkg = _make_pkg(
            replay_manifest="sha256::out",
            merged_content_digest="sha256::out",
        )
        prov = _build_g24_provenance(sealed, prompt, pkg)
        evidence = {"g24_provenance": prov}
        verdict = evaluate_g24(
            "G24", self._gate_def(), pkg, evidence,
            "req-test-001", "run-test-001", "trace-test-001",
        )
        assert verdict.result == VERDICT_PASS, (
            f"Expected PASS but got {verdict.result}. "
            f"Reason codes: {verdict.reason_codes}"
        )

    def test_unknown_when_required_field_missing(self):
        from agentic_core.runtime.gates.gate_evaluators import VERDICT_UNKNOWN
        pkg = _make_pkg(replay_manifest="sha256::real")
        evidence = {
            "g24_provenance": {
                "replay_key": "sha256::real",
                # resume_candidate_profile_hash missing
                "output_artifact_digest": "sha256::real",
            }
        }
        verdict = evaluate_g24(
            "G24", self._gate_def(), pkg, evidence,
            "req-1", "run-1", "trace-1",
        )
        assert verdict.result == VERDICT_UNKNOWN

    def test_unknown_when_no_evidence(self):
        from agentic_core.runtime.gates.gate_evaluators import VERDICT_UNKNOWN
        pkg = _make_pkg(replay_manifest="")  # no replay_key
        evidence = {}
        gate_def = {
            "gate_id": "G24",
            "severity": "hard",
            "required_provenance_fields": ["replay_key"],
        }
        verdict = evaluate_g24(
            "G24", gate_def, pkg, evidence,
            "req-1", "run-1", "trace-1",
        )
        assert verdict.result == VERDICT_UNKNOWN


# ── E. exit_finalize_apps_rg passes evidence to harness ──────────────────────

class TestExitFinalizePassesEvidence:
    """E. Integration: exit_finalize_apps_rg populates evidence and passes it to harness."""

    def test_harness_evaluate_called_with_evidence_dict(self, tmp_path):
        """harness.evaluate() receives a dict with g22_rubric_scores and g24_provenance."""
        from agentic_core.runtime.exit.apps_rg_exit_binding import (
            exit_finalize_apps_rg,
        )

        resume_json = json.dumps({
            "schema_version": "master_resume_v2.16",
            "executive_summary": "Senior engineering leader.",
            "experience": [{"company": "Acme", "title": "SVP"}],
            "education": [{"degree": "BS CS"}],
            "skills": ["Python"],
        })
        sealed = _make_sealed(
            generated_content=resume_json,
            compilation_hash="sha256::out001",
        )
        prompt = _make_prompt(
            evidence_digest="sha256::fec001",
            compilation_hash="sha256::prompt001",
        )

        captured_evidence: dict = {}

        def capture_evaluate(pkg, *, evidence=None, **kwargs):
            nonlocal captured_evidence
            captured_evidence = evidence or {}
            from agentic_core.runtime.exit.exit_gate_harness import (
                ExitDispositionReceipt,
            )
            from agentic_core.runtime.gates.gate_mesh import GateMeshResult
            from agentic_core.runtime.exit.exit_disposition import RuntimeExhaustBundle
            receipt = MagicMock(spec=ExitDispositionReceipt)
            receipt.decisive_blocker_gate_ids = []
            receipt.hard_fail_count = 0
            receipt.unknown_count = 0
            receipt.disposition = "finish"
            mesh_result = MagicMock(spec=GateMeshResult)
            exhaust = MagicMock(spec=RuntimeExhaustBundle)
            return receipt, mesh_result, exhaust

        mock_harness = MagicMock()
        mock_harness.evaluate.side_effect = capture_evaluate

        with patch(
            "agentic_core.runtime.exit.apps_rg_exit_binding.build_apps_rg_exit_harness",
            return_value=mock_harness,
        ), patch(
            "agentic_core.runtime.exit.apps_rg_exit_binding._resolve_repo_root",
            return_value=tmp_path,
        ):
            (tmp_path / "artifacts" / "apps_rg" / "runs").mkdir(parents=True, exist_ok=True)
            (tmp_path / "apps_rg" / "config" / "domain_contract").mkdir(parents=True, exist_ok=True)
            exit_finalize_apps_rg(sealed, prompt)

        assert mock_harness.evaluate.called, "harness.evaluate() was not called"
        assert "g22_rubric_scores" in captured_evidence, (
            "evidence dict missing g22_rubric_scores"
        )
        assert "g24_provenance" in captured_evidence, (
            "evidence dict missing g24_provenance"
        )
        assert "g28" in captured_evidence, "evidence dict missing g28"

    def test_g22_rubric_scores_non_empty_for_valid_json(self, tmp_path):
        """g22_rubric_scores is non-empty when parsed_content is valid JSON."""
        from agentic_core.runtime.exit.apps_rg_exit_binding import (
            exit_finalize_apps_rg,
        )

        resume_json = json.dumps({
            "executive_summary": "VP of Engineering",
            "experience": [],
            "education": [],
            "skills": [],
        })
        sealed = _make_sealed(generated_content=resume_json)
        prompt = _make_prompt()

        captured_evidence: dict = {}

        def capture_evaluate(pkg, *, evidence=None, **kwargs):
            nonlocal captured_evidence
            captured_evidence = evidence or {}
            from agentic_core.runtime.exit.exit_gate_harness import ExitDispositionReceipt
            receipt = MagicMock(spec=ExitDispositionReceipt)
            receipt.decisive_blocker_gate_ids = []
            receipt.hard_fail_count = 0
            receipt.unknown_count = 0
            receipt.disposition = "finish"
            from agentic_core.runtime.gates.gate_mesh import GateMeshResult
            from agentic_core.runtime.exit.exit_disposition import RuntimeExhaustBundle
            return receipt, MagicMock(spec=GateMeshResult), MagicMock(spec=RuntimeExhaustBundle)

        mock_harness = MagicMock()
        mock_harness.evaluate.side_effect = capture_evaluate

        with patch(
            "agentic_core.runtime.exit.apps_rg_exit_binding.build_apps_rg_exit_harness",
            return_value=mock_harness,
        ), patch(
            "agentic_core.runtime.exit.apps_rg_exit_binding._resolve_repo_root",
            return_value=tmp_path,
        ):
            (tmp_path / "artifacts" / "apps_rg" / "runs").mkdir(parents=True, exist_ok=True)
            (tmp_path / "apps_rg" / "config" / "domain_contract").mkdir(parents=True, exist_ok=True)
            exit_finalize_apps_rg(sealed, prompt)

        scores = captured_evidence.get("g22_rubric_scores", {})
        assert scores, "g22_rubric_scores should be non-empty for valid JSON input"
        assert "format_compliance" in scores

    def test_g24_provenance_has_real_hashes(self, tmp_path):
        """g24_provenance uses real hashes from sealed + prompt artifacts."""
        from agentic_core.runtime.exit.apps_rg_exit_binding import (
            exit_finalize_apps_rg,
        )

        resume_json = json.dumps({"executive_summary": "Real content."})
        sealed = _make_sealed(
            generated_content=resume_json,
            compilation_hash="sha256::sealed-real",
        )
        prompt = _make_prompt(
            evidence_digest="sha256::fec-real",
            compilation_hash="sha256::prompt-real",
        )

        captured_evidence: dict = {}

        def capture_evaluate(pkg, *, evidence=None, **kwargs):
            nonlocal captured_evidence
            captured_evidence = evidence or {}
            from agentic_core.runtime.exit.exit_gate_harness import ExitDispositionReceipt
            receipt = MagicMock(spec=ExitDispositionReceipt)
            receipt.decisive_blocker_gate_ids = []
            receipt.hard_fail_count = 0
            receipt.unknown_count = 0
            receipt.disposition = "finish"
            from agentic_core.runtime.gates.gate_mesh import GateMeshResult
            from agentic_core.runtime.exit.exit_disposition import RuntimeExhaustBundle
            return receipt, MagicMock(spec=GateMeshResult), MagicMock(spec=RuntimeExhaustBundle)

        mock_harness = MagicMock()
        mock_harness.evaluate.side_effect = capture_evaluate

        with patch(
            "agentic_core.runtime.exit.apps_rg_exit_binding.build_apps_rg_exit_harness",
            return_value=mock_harness,
        ), patch(
            "agentic_core.runtime.exit.apps_rg_exit_binding._resolve_repo_root",
            return_value=tmp_path,
        ):
            (tmp_path / "artifacts" / "apps_rg" / "runs").mkdir(parents=True, exist_ok=True)
            (tmp_path / "apps_rg" / "config" / "domain_contract").mkdir(parents=True, exist_ok=True)
            exit_finalize_apps_rg(sealed, prompt)

        prov = captured_evidence.get("g24_provenance", {})
        # No per-input hashes in component_hash_map → _safe_build_g24_provenance returns {}
        # G24 should receive empty dict (UNKNOWN), NOT a false value from evidence_digest.
        assert prov == {}, (
            f"Expected empty g24_provenance when per-input hashes are absent, got: {prov}"
        )

    def test_g22_and_g24_evidence_is_built_by_apps_rg_code(self, tmp_path):
        """g22 and g24 evidence is produced by apps_rg-owned builders, not core."""
        import inspect
        from apps_rg.exit.apps_rg_exit_evidence_builder import (
            compute_g22_rubric_scores,
            build_g24_provenance,
        )
        for fn in [compute_g22_rubric_scores, build_g24_provenance]:
            src = inspect.getfile(fn)
            assert "apps_rg" in src.replace("\\", "/"), (
                f"{fn.__name__} must be defined under apps_rg/, found at {src}"
            )


# ── T. seal_resume_sections — section sealer tests (T1-T9) ───────────────────

from apps_rg.exit.apps_rg_exit_evidence_builder import seal_resume_sections


_FULL_RESUME = {
    "executive_summary": {"content": ["SVP with 15 years AI platform experience."]},
    "experience": [{"company": "Unify Consulting", "title": "SVP Engineering",
                    "dates": "2023-Present"}],
    "skills": ["AI/data platform", "enterprise architecture"],
    "education": [{"degree": "MS Biostatistics", "institution": "Columbia"}],
    "certifications": [{"name": "AWS ML Engineer", "issuer": "AWS", "year": 2025}],
    "target_company": "Brown & Brown",
    "target_role": "SVP IT Strategy & Innovation",
    "target_level": "EXECUTIVE",
}


class TestSealResumeSections:
    """T1-T9: seal_resume_sections maps L2 flat keys to canonical sealed sections."""

    def test_t1_l2_keys_map_to_canonical_ids(self):
        """T1: L2 flat keys produce SealedSectionArtifacts with canonical node_ids."""
        sections = seal_resume_sections(_FULL_RESUME, "run-t1")
        node_ids = {s.node_id for s in sections}
        assert "professional_summary" in node_ids, "executive_summary → professional_summary"
        assert "experience_block" in node_ids, "experience → experience_block"
        assert "skills_block" in node_ids, "skills → skills_block"
        assert "education_block" in node_ids, "education → education_block"
        assert "certifications_block" in node_ids, "certifications → certifications_block"

    def test_t2_sealed_sections_nonempty_for_real_content(self):
        """T2: sealed_sections is non-empty when generated_resume has real content."""
        sections = seal_resume_sections(_FULL_RESUME, "run-t2")
        assert len(sections) >= 4, (
            f"Expected at least 4 sealed sections, got {len(sections)}"
        )

    def test_t3_merged_content_from_generated_content(self, tmp_path):
        """T3: merged_content is populated from sealed.generated_content in SealedWorkflowPackage."""
        from unittest.mock import patch
        from agentic_core.runtime.exit.apps_rg_exit_binding import exit_finalize_apps_rg

        resume_json = json.dumps(_FULL_RESUME)
        sealed = _make_sealed(generated_content=resume_json, run_id="run-t3")
        prompt = _make_prompt()

        captured_pkg = {}

        def capture_evaluate(pkg, *, evidence=None, **kwargs):
            captured_pkg["pkg"] = pkg
            from unittest.mock import MagicMock
            from agentic_core.runtime.exit.exit_gate_harness import ExitDispositionReceipt
            from agentic_core.runtime.gates.gate_mesh import GateMeshResult
            from agentic_core.runtime.exit.exit_disposition import RuntimeExhaustBundle
            receipt = MagicMock(spec=ExitDispositionReceipt)
            receipt.decisive_blocker_gate_ids = []
            receipt.hard_fail_count = 0
            receipt.unknown_count = 0
            receipt.disposition = "finish"
            return receipt, MagicMock(spec=GateMeshResult), MagicMock(spec=RuntimeExhaustBundle)

        mock_harness = MagicMock()
        mock_harness.evaluate.side_effect = capture_evaluate

        with patch(
            "agentic_core.runtime.exit.apps_rg_exit_binding.build_apps_rg_exit_harness",
            return_value=mock_harness,
        ), patch(
            "agentic_core.runtime.exit.apps_rg_exit_binding._resolve_repo_root",
            return_value=tmp_path,
        ):
            (tmp_path / "artifacts" / "apps_rg" / "runs").mkdir(parents=True, exist_ok=True)
            exit_finalize_apps_rg(sealed, prompt)

        pkg = captured_pkg.get("pkg")
        assert pkg is not None, "SealedWorkflowPackage not captured"
        assert pkg.merged_content == resume_json, (
            "merged_content must equal sealed.generated_content"
        )

    def test_t4_g21_sections_present_for_mapped_keys(self):
        """T4: sections present in L2 output are sealed and satisfy G21 required list."""
        sections = seal_resume_sections(_FULL_RESUME, "run-t4")
        node_ids = {s.node_id for s in sections}
        # G21 requires: professional_summary, experience_block, skills_block,
        # education_block, header_block.  All except header_block should now pass.
        for expected in ("professional_summary", "experience_block",
                         "skills_block", "education_block"):
            assert expected in node_ids, f"G21 required section {expected!r} not sealed"

    def test_t5_header_block_not_fabricated_from_target_fields(self):
        """T5: header_block must NOT appear when only target_company/role/level are present."""
        content_no_header = {
            "executive_summary": "Summary.",
            "experience": [],
            "skills": [],
            "education": [],
            "target_company": "ACME",      # must NOT trigger header_block
            "target_role": "SVP",           # must NOT trigger header_block
            "target_level": "EXECUTIVE",    # must NOT trigger header_block
        }
        sections = seal_resume_sections(content_no_header, "run-t5")
        node_ids = {s.node_id for s in sections}
        assert "header_block" not in node_ids, (
            "header_block must NOT be synthesised from target_company/role/level fields"
        )

    def test_t5b_header_block_created_from_real_header_field(self):
        """T5b: header_block IS created when a real 'header' dict is present."""
        content_with_header = {
            "header": {"name": "Amit Ayer", "email": "a@example.com"},
            "executive_summary": "Summary.",
            "experience": [],
            "skills": [],
            "education": [],
        }
        sections = seal_resume_sections(content_with_header, "run-t5b")
        node_ids = {s.node_id for s in sections}
        assert "header_block" in node_ids, (
            "header_block should be created when 'header' key contains real candidate data"
        )

    def test_t6_g26_sealed_sections_real_content(self, tmp_path):
        """T6: G26 passes only when sealed_sections or merged_content are real."""
        from agentic_core.runtime.gates.gate_evaluators import evaluate_g26, VERDICT_PASS
        from agentic_core.runtime.contracts.sealed_workflow_types import SealedWorkflowPackage

        resume_json = json.dumps(_FULL_RESUME)
        sections = seal_resume_sections(_FULL_RESUME, "run-t6")
        pkg = SealedWorkflowPackage(
            package_id="pkg::apps_rg::run-t6",
            run_id="run-t6",
            trace_root="trace-t6",
            route_contract_ref="rcr::apps_rg::resume_generation::v1",
            workflow_ref="wfm::apps_rg::resume_generation::v1",
            workflow_manifest_ref="wfm::apps_rg::resume_generation::v1",
            sealed_sections=sections,
            merged_content=resume_json,
            merged_content_digest="sha256::t6",
            merged_payload_digest="sha256::t6",
            replay_manifest="sha256::t6",
        )
        import json as _json
        gate_def = _json.loads(
            (tmp_path.parent.parent.parent / "c:\\Git\\Agentic-Workflow-FRESH"
             if False else
             __import__("pathlib").Path(
                 "apps_rg/config/domain_contract/exit_profile.resume_generation.v1.json"
             )).read_text()
        )["gate_definitions"]["G26"] if False else {
            "gate_id": "G26",
            "severity": "hard_fail",
        }
        verdict = evaluate_g26("G26", gate_def, pkg, {}, "req-t6", "run-t6", "trace-t6")
        assert verdict.result == VERDICT_PASS, (
            f"G26 must PASS when sealed_sections and merged_content are real. "
            f"Got {verdict.result}: {verdict.reason_codes}"
        )

    def test_t7_role_alignment_computed_from_content(self):
        """T7: role_alignment score is > 0 for executive IT summary text."""
        sealed = _make_sealed()
        content = {
            "executive_summary": {
                "content": [
                    "Strategic technology leader with expertise in enterprise architecture, "
                    "AI platform delivery, digital transformation, and governance."
                ]
            },
            "experience": [],
            "education": [],
            "skills": ["strategy", "leadership"],
        }
        scores = _compute_deterministic_dim_scores(content, sealed)
        assert "role_alignment" in scores, "role_alignment must be in scores"
        assert scores["role_alignment"] > 0.0, (
            f"role_alignment should be > 0 for executive IT content, got {scores['role_alignment']}"
        )

    def test_t7b_specificity_computed_from_numeric_content(self):
        """T7b: specificity score > 0 when content contains numeric evidence."""
        sealed = _make_sealed()
        content = {
            "executive_summary": "Led 12 platform migrations over 8 years, achieving 40% cost reduction.",
            "experience": [
                {"company": "Acme", "dates": "2018-2023",
                 "achievements": ["Reduced costs by $2M", "Scaled to 500 users"]}
            ],
            "education": [],
            "skills": [],
        }
        scores = _compute_deterministic_dim_scores(content, sealed)
        assert "specificity" in scores, "specificity must be in scores"
        assert scores["specificity"] > 0.0, (
            f"specificity should be > 0 when numeric tokens are present, got {scores['specificity']}"
        )

    def test_t8_factual_grounding_absent_from_scores(self):
        """T8: factual_grounding must be absent — requires real source-resume comparison."""
        sealed = _make_sealed()
        scores = _compute_deterministic_dim_scores(_FULL_RESUME, sealed)
        assert "factual_grounding" not in scores, (
            "factual_grounding must NOT be computed without real C0/source-resume evidence"
        )

    def test_t9_g22_remains_unknown_when_factual_grounding_required(self):
        """T9: G22 stays UNKNOWN when factual_grounding is required by profile but absent."""
        from agentic_core.runtime.gates.gate_evaluators import evaluate_g22, VERDICT_UNKNOWN
        from agentic_core.runtime.contracts.sealed_workflow_types import SealedWorkflowPackage

        pkg = _make_pkg()
        # Gate def requires factual_grounding — simulating the real exit profile
        gate_def = {
            "gate_id": "G22",
            "severity": "hard_fail",
            "dimension_thresholds": {
                "factual_grounding": 0.95,          # required, not informational_only
                "role_alignment": 0.65,
                "format_compliance": 0.95,
            },
        }
        # Scores from deterministic scorer — factual_grounding will be absent
        scores = _compute_deterministic_dim_scores(_FULL_RESUME, _make_sealed())
        assert "factual_grounding" not in scores, "Pre-condition: factual_grounding must be absent"

        evidence = {"g22_rubric_scores": scores}
        verdict = evaluate_g22("G22", gate_def, pkg, evidence, "req-t9", "run-t9", "trace-t9")
        assert verdict.result == VERDICT_UNKNOWN, (
            f"G22 must remain UNKNOWN when factual_grounding is required and absent. "
            f"Got: {verdict.result} reason_codes={verdict.reason_codes}"
        )

    def test_t2_none_content_returns_empty_tuple(self):
        """T2b: seal_resume_sections returns () when content is None."""
        assert seal_resume_sections(None, "run-none") == ()

    def test_t2_empty_dict_returns_empty_tuple(self):
        """T2c: seal_resume_sections returns () when content is empty dict."""
        assert seal_resume_sections({}, "run-empty") == ()

    def test_section_artifacts_have_real_digests(self):
        """Each SealedSectionArtifact must carry a non-empty SHA-256 content_digest."""
        import hashlib
        sections = seal_resume_sections(_FULL_RESUME, "run-digest")
        for s in sections:
            assert s.content_digest, f"content_digest empty for section {s.node_id}"
            assert len(s.content_digest) == 64, (
                f"content_digest for {s.node_id} is not a 64-char hex SHA-256"
            )
            # Verify the digest matches the content
            expected = hashlib.sha256(s.sealed_content.encode("utf-8")).hexdigest()
            assert s.content_digest == expected, (
                f"Digest mismatch for {s.node_id}"
            )

    def test_section_payload_ref_points_to_l2_key(self):
        """payload_ref must reference the L2 source key for traceability."""
        sections = seal_resume_sections(_FULL_RESUME, "run-ref")
        for s in sections:
            assert s.payload_ref.startswith("generated_resume.json#"), (
                f"payload_ref for {s.node_id} must start with 'generated_resume.json#', "
                f"got: {s.payload_ref!r}"
            )

    def test_run_id_threaded_into_sections(self):
        """run_id from the sealed artifact is threaded into every SealedSectionArtifact."""
        sections = seal_resume_sections(_FULL_RESUME, "run-thread-xyz")
        for s in sections:
            assert s.run_id == "run-thread-xyz", (
                f"run_id not threaded into section {s.node_id}"
            )


# ── G FactualGrounding diagnostics (Patch A + B tests) ───────────────────────


def _make_fec(sources_and_contents: list[tuple[str, str]]) -> MagicMock:
    """Build a minimal FinalEvidenceContract mock with evidence_items."""
    fec = MagicMock()
    items = []
    for src, content in sources_and_contents:
        item = MagicMock()
        item.source = src
        item.content = content
        items.append(item)
    fec.evidence_items = items
    return fec


_EVIDENCE_RESUME = "John Smith SVP Engineering led digital transformation 2018 2022 strategy"
_EVIDENCE_JD = "seeking SVP Engineering digital innovation strategy leadership"

_GENERATED_RESUME_GROUNDED = {
    "executive_summary": "John Smith SVP Engineering 2018 strategy digital transformation",
    "experience": [{"title": "SVP Engineering", "years": "2018-2022"}],
    "skills": ["leadership", "strategy"],
    "education": [{"degree": "BS Computer Science"}],
}

_GENERATED_RESUME_PARTIALLY_UNGROUNDED = {
    "executive_summary": "John Smith invented quantum blockchain disruption paradigms",
    "experience": [{"title": "SVP Engineering", "years": "2018-2022"}],
    "skills": ["leadership", "strategy"],
    "education": [{"degree": "BS Computer Science"}],
}


class TestFactualGroundingDiagnostics:
    """Tests 1-6: compute_factual_grounding returns FactualGroundingResult."""

    def test_1_returns_factual_grounding_result_instance(self):
        """Test 1: compute_factual_grounding returns FactualGroundingResult, not float."""
        fec = _make_fec([
            ("resume:source", _EVIDENCE_RESUME),
            ("jd:source", _EVIDENCE_JD),
        ])
        result = _compute_factual_grounding(_GENERATED_RESUME_GROUNDED, fec)
        assert result is not None
        assert isinstance(result, FactualGroundingResult), (
            f"Expected FactualGroundingResult, got {type(result).__name__}"
        )

    def test_2_score_is_float_in_range(self):
        """Test 2: score attribute is a float in [0.0, 1.0]."""
        fec = _make_fec([("resume:source", _EVIDENCE_RESUME)])
        result = _compute_factual_grounding(_GENERATED_RESUME_GROUNDED, fec)
        assert result is not None
        assert isinstance(result.score, float)
        assert 0.0 <= result.score <= 1.0

    def test_3_g22_still_fails_when_score_below_threshold(self):
        """Test 3: G22 remains FAIL when factual_grounding < 0.950; diagnostics don't change verdict."""
        from agentic_core.runtime.gates.gate_types import VERDICT_FAIL

        fec = _make_fec([
            ("resume:source", "short evidence only five words here"),
        ])
        # Content with many tokens not in evidence → low score
        content = {
            "executive_summary": "invented quantum blockchain disruption paradigms synergized",
            "experience": [{"title": "architect"}],
            "skills": ["quantum", "blockchain"],
            "education": [{"degree": "PhD"}],
        }
        result = _compute_factual_grounding(content, fec)
        assert result is not None
        # Build evidence dict as the binding would
        scores = _compute_deterministic_dim_scores(content, MagicMock())
        scores["factual_grounding"] = result.score

        gate_def = {
            "dimension_thresholds": {
                "factual_grounding": 0.950,
                "format_compliance": 0.0,
                "ats_readability": 0.0,
                "no_fabrication": 0.0,
                "concision": 0.0,
                "role_alignment": 0.0,
                "specificity": 0.0,
            }
        }
        from agentic_core.runtime.contracts.sealed_workflow_types import SealedWorkflowPackage
        pkg = SealedWorkflowPackage(
            package_id="pkg::test", run_id="run-t3", trace_root="trace-t3",
            route_contract_ref="rcr::test", workflow_ref="wfm::test",
            workflow_manifest_ref="wfm::test", sealed_sections=(),
            section_count=0, merged_content="", merged_content_digest="",
            merged_payload_digest="", replay_manifest="",
        )
        verdict = evaluate_g22("G22", gate_def, pkg, {"g22_rubric_scores": scores},
                               "req-t3", "run-t3", "trace-t3")
        # Score well below 0.950 → must be FAIL
        if result.score < 0.950:
            assert verdict.result == VERDICT_FAIL, (
                f"G22 must FAIL when factual_grounding={result.score} < 0.950; "
                f"got {verdict.result}"
            )

    def test_4_unsupported_samples_present_when_score_lt_1(self):
        """Test 4: unsupported_token_samples is non-empty when score < 1.0."""
        fec = _make_fec([("resume:source", _EVIDENCE_RESUME)])
        result = _compute_factual_grounding(_GENERATED_RESUME_PARTIALLY_UNGROUNDED, fec)
        assert result is not None
        if result.score < 1.0:
            assert len(result.unsupported_token_samples) > 0, (
                f"unsupported_token_samples must be non-empty when score={result.score} < 1.0"
            )

    def test_5_supported_samples_present_when_evidence_matches(self):
        """Test 5: supported_token_samples is non-empty when evidence covers generated tokens."""
        fec = _make_fec([
            ("resume:source", _EVIDENCE_RESUME),
            ("jd:source", _EVIDENCE_JD),
        ])
        result = _compute_factual_grounding(_GENERATED_RESUME_GROUNDED, fec)
        assert result is not None
        assert len(result.supported_token_samples) > 0, (
            "supported_token_samples must be non-empty when evidence matches generated content"
        )

    def test_6_source_evidence_refs_populated_when_fec_has_items(self):
        """Test 6: source_evidence_refs lists the FEC item sources that were used."""
        fec = _make_fec([
            ("resume:app_payload.source_resume_text", _EVIDENCE_RESUME),
            ("jd:app_payload.jd_text", _EVIDENCE_JD),
        ])
        result = _compute_factual_grounding(_GENERATED_RESUME_GROUNDED, fec)
        assert result is not None
        assert len(result.source_evidence_refs) == 2
        assert "resume:app_payload.source_resume_text" in result.source_evidence_refs
        assert "jd:app_payload.jd_text" in result.source_evidence_refs

    def test_7_fec_none_returns_none_no_fabrication(self):
        """Test 7: fec=None returns None — no diagnostics fabricated."""
        result = _compute_factual_grounding(_GENERATED_RESUME_GROUNDED, None)
        assert result is None, (
            "compute_factual_grounding must return None when fec=None, not a fabricated result"
        )

    def test_8_sample_lists_bounded_by_limit(self):
        """Test 8: supported and unsupported sample lists are bounded by _FG_SAMPLE_LIMIT."""
        from apps_rg.exit.apps_rg_exit_evidence_builder import _FG_SAMPLE_LIMIT
        # Large content with many unique tokens
        big_content = {
            "executive_summary": " ".join(f"word{i}" for i in range(200)),
            "experience": [], "skills": [], "education": [],
        }
        fec = _make_fec([("resume:source", "word1 word2 word3 word4 word5")])
        result = _compute_factual_grounding(big_content, fec)
        assert result is not None
        assert len(result.supported_token_samples) <= _FG_SAMPLE_LIMIT, (
            f"supported_token_samples exceeded _FG_SAMPLE_LIMIT={_FG_SAMPLE_LIMIT}"
        )
        assert len(result.unsupported_token_samples) <= _FG_SAMPLE_LIMIT, (
            f"unsupported_token_samples exceeded _FG_SAMPLE_LIMIT={_FG_SAMPLE_LIMIT}"
        )

    def test_8b_excluded_structural_tokens_present_for_schema_fields(self):
        """Test 8b: structural/control key values (target_company, schema_version, etc.)
        are excluded from scoring and appear in excluded_structural_tokens for diagnostics."""
        from apps_rg.exit.apps_rg_exit_evidence_builder import _FG_SAMPLE_LIMIT
        content = {
            "executive_summary": "senior engineering leader with cloud experience",
            "target_company": "BrownAndBrown",
            "target_role": "SVPStrategyXYZ",
            "schema_version": "uniqueschematoken123",
            "stub_mode": False,
            "experience": [],
            "skills": [],
        }
        fec = _make_fec([("resume:source", "senior engineering leader cloud experience")])
        result = _compute_factual_grounding(content, fec)
        assert result is not None
        # excluded_structural_tokens field must exist
        assert hasattr(result, "excluded_structural_tokens"), (
            "FactualGroundingResult must have excluded_structural_tokens field"
        )
        # The unique control tokens must not appear in unsupported_token_samples
        unsupported_set = set(result.unsupported_token_samples)
        for tok in ("brownandbrown", "svpstrategyxyz", "uniqueschematoken123"):
            assert tok not in unsupported_set, (
                f"Control token '{tok}' leaked into unsupported_token_samples — "
                "structural exclusion is not working"
            )
        # excluded_structural_tokens list must be bounded
        assert len(result.excluded_structural_tokens) <= _FG_SAMPLE_LIMIT


def _make_harness_mock(
    run_id: str = "run-test-001",
    request_id: str = "req-test-001",
) -> MagicMock:
    """Build a harness mock whose evaluate() returns serialization-safe objects."""
    from agentic_core.runtime.exit.exit_gate_harness import ExitDispositionReceipt
    from agentic_core.runtime.exit.exit_disposition import (
        RuntimeExhaustBundle,
        X3D_ALLOW_FINISH,
    )
    from agentic_core.runtime.gates.gate_types import (
        GateVerdict,
        GateMeshResult,
        VERDICT_WARN,
    )

    _g28_verdict = GateVerdict(
        gate_id="G28",
        gate_family="audit",
        result=VERDICT_WARN,
        score=0.0,
        remediation_hint="missing gate_mesh_result_ref",
        deterministic_digest="sha256::g28::warn",
        schema_version="1.0",
    )
    _mesh_result = GateMeshResult(
        request_id=request_id,
        run_id=run_id,
        verdicts=(_g28_verdict,),
        required_gate_ids=("G21", "G22", "G23", "G24", "G26", "G28"),
        gate_mesh_schema_version="1.0",
        trace_root="trace-test",
    )

    _receipt_dict = {
        "schema_version": "1.0",
        "request_id": request_id,
        "run_id": run_id,
        "x3_code": X3D_ALLOW_FINISH,
        "allows_finish": True,
        "hard_fail_count": 0,
        "unknown_count": 0,
        "decisive_blocker_gate_ids": [],
        "decisive_reason": "all gates pass",
        "gate_mesh_result_ref": "sha256::mesh::abc",
        "gate_verdict_refs": [],
    }
    receipt = MagicMock(spec=ExitDispositionReceipt)
    receipt.as_json.return_value = json.dumps(_receipt_dict)
    receipt.decisive_blocker_gate_ids = []
    receipt.hard_fail_count = 0
    receipt.unknown_count = 0
    receipt.allows_finish = True
    receipt.x3_code = X3D_ALLOW_FINISH
    receipt.gate_mesh_result_ref = "sha256::mesh::abc"
    receipt.decisive_reason = "all gates pass"

    exhaust = MagicMock(spec=RuntimeExhaustBundle)

    mock_harness = MagicMock()
    mock_harness.evaluate.return_value = (receipt, _mesh_result, exhaust)
    # _profile.gate_definitions["G28"] must exist for post-mesh pass-2
    mock_harness._profile = MagicMock()
    mock_harness._profile.gate_definitions = {
        "G28": {
            "required_audit_refs": ["sealed_workflow_package_ref", "gate_mesh_result_ref"]
        }
    }
    return mock_harness


class TestReceiptDualG28:
    """Tests 9-10: 07_gate_receipt.json written after pass-2 with both G28 verdicts."""

    def test_9_receipt_contains_g28_audit_chain(self, tmp_path):
        """Test 9: 07_gate_receipt.json includes g28_audit_chain with both verdict fields."""
        from agentic_core.runtime.exit.apps_rg_exit_binding import exit_finalize_apps_rg

        run_id = "run-receipt-test"
        sealed = _make_sealed(
            generated_content=json.dumps(_FULL_RESUME),
            run_id=run_id,
        )
        prompt = _make_prompt()
        mock_harness = _make_harness_mock(run_id=run_id)

        with patch(
            "agentic_core.runtime.exit.apps_rg_exit_binding.build_apps_rg_exit_harness",
            return_value=mock_harness,
        ), patch(
            "agentic_core.runtime.exit.apps_rg_exit_binding._resolve_repo_root",
            return_value=tmp_path,
        ):
            (tmp_path / "artifacts" / "apps_rg" / "runs").mkdir(parents=True, exist_ok=True)
            exit_finalize_apps_rg(sealed, prompt, fec=None)

        runs_base = tmp_path / "artifacts" / "apps_rg" / "runs"
        run_dirs = [d for d in runs_base.iterdir() if d.is_dir()]
        assert run_dirs, "No run directory created"
        run_dir = run_dirs[0]

        receipt_path = run_dir / "07_gate_receipt.json"
        assert receipt_path.exists(), "07_gate_receipt.json not written"

        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        assert "g28_audit_chain" in receipt, (
            "07_gate_receipt.json must contain 'g28_audit_chain' key after Patch B"
        )
        chain = receipt["g28_audit_chain"]
        assert "g28_initial_verdict" in chain, "g28_audit_chain must have g28_initial_verdict"
        assert "g28_post_mesh_verdict" in chain, "g28_audit_chain must have g28_post_mesh_verdict"

    def test_10_diagnostics_artifact_written_when_fec_present(self, tmp_path):
        """Test 10: 07_g22_factual_grounding_diagnostics.json written when FEC provided."""
        from agentic_core.runtime.exit.apps_rg_exit_binding import exit_finalize_apps_rg

        run_id = "run-diag-test"
        sealed = _make_sealed(
            generated_content=json.dumps(_GENERATED_RESUME_GROUNDED),
            run_id=run_id,
        )
        prompt = _make_prompt()
        fec = _make_fec([
            ("resume:source", _EVIDENCE_RESUME),
            ("jd:source", _EVIDENCE_JD),
        ])
        mock_harness = _make_harness_mock(run_id=run_id)

        with patch(
            "agentic_core.runtime.exit.apps_rg_exit_binding.build_apps_rg_exit_harness",
            return_value=mock_harness,
        ), patch(
            "agentic_core.runtime.exit.apps_rg_exit_binding._resolve_repo_root",
            return_value=tmp_path,
        ):
            (tmp_path / "artifacts" / "apps_rg" / "runs").mkdir(parents=True, exist_ok=True)
            exit_finalize_apps_rg(sealed, prompt, fec=fec)

        runs_base = tmp_path / "artifacts" / "apps_rg" / "runs"
        run_dirs = [d for d in runs_base.iterdir() if d.is_dir()]
        assert run_dirs, "No run directory created"
        run_dir = run_dirs[0]

        diag_path = run_dir / "07_g22_factual_grounding_diagnostics.json"
        assert diag_path.exists(), (
            "07_g22_factual_grounding_diagnostics.json must be written when FEC is present"
        )
        diag = json.loads(diag_path.read_text(encoding="utf-8"))
        assert diag["gate_id"] == "G22"
        assert diag["dimension"] == "factual_grounding"
        assert "score" in diag
        assert "supported_token_samples" in diag
        assert "unsupported_token_samples" in diag
        assert "source_evidence_refs" in diag
        assert "decisive_reason" in diag
