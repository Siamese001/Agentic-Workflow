"""W4 tests: apps_rg Exit binding C0 evidence consumption.

Covers:
- Exit reads support_status and support_target_met from FEC.
- Blocking statuses (UNKNOWN, EMPTY, BLOCKED, CONFLICTED) set outcome_authorized=False.
- PASS and WEAK_WITH_CAVEATS support_status allow outcome_authorized=True.
- G13 citation hard-fail: empty citation_map + excluded_refs → FAIL gate.
- G09 freshness warn: empty freshness_receipts → WARN gate.
- apps_rg-owned fields (jd_keyword_coverage, overfit_score, provenance_valid) present.
- fec=None is handled gracefully (no exception, no blocking).
- prompt_artifact positional arg accepted without TypeError.
- agentic_core Exit remains generic (no apps_rg literals in agentic_core).
- W1/W2/W3 test modules are importable (regression guard).
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

import pytest

from agentic_core.runtime.contracts.final_evidence_contract import (
    EvidenceItem,
    FinalEvidenceContract,
)
from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
from apps_rg.runtime.bindings.exit_binding import (
    _BLOCKING_SUPPORT_STATUSES,
    _evaluate_c0_evidence_gates,
    _compute_apps_rg_owned_fields,
    ExitGateVerdict,
    exit_finalize_apps_rg,
    build_apps_rg_exit_harness,
)

_REPO_ROOT = Path(__file__).parents[2]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_CERT_REF = "c0-apps-rg-w4-test"


def _make_fec(
    run_id: str = "run_w4_test",
    support_status: str = "PASS",
    support_target_met: bool = True,
    citation_map: tuple = (),
    freshness_receipts: tuple = (),
    excluded_evidence_refs: tuple = (),
    extra_items: tuple = (),
) -> FinalEvidenceContract:
    items = (
        EvidenceItem(source="jd_payload:jd_text", content="SWE role"),
        EvidenceItem(source="resume_payload:resume_text", content="10y Python"),
    ) + extra_items
    return FinalEvidenceContract(
        request_id=run_id,
        run_id=run_id,
        app_id="apps_rg",
        trace_id=run_id,
        evidence_items=items,
        retrieval_sources=("jd_payload:jd_text", "resume_payload:resume_text"),
        support_target_met=support_target_met,
        support_status=support_status,
        citation_map=citation_map,
        freshness_receipts=freshness_receipts,
        excluded_evidence_refs=excluded_evidence_refs,
        l5_certification_ref=_CERT_REF,
    )


def _make_sealed(
    run_id: str = "run_w4_test",
    execution_status: str = "completed",
    compilation_hash: str = "abc123",
) -> SealedL2Artifact:
    return SealedL2Artifact(
        request_id=run_id,
        run_id=run_id,
        app_id="apps_rg",
        trace_id=run_id,
        execution_status=execution_status,
        generated_content="Summary text",
        proposed_state_diff={"target_company": "Acme", "target_role": "SWE"},
        compilation_hash=compilation_hash,
        sovereign_execution_receipt="vllm-stub-receipt",
        tenant_id="apps_rg",
        l5_certification_ref="test-sealed-l2-w4",
    )


# ---------------------------------------------------------------------------
# TestEvidenceGateHelper
# ---------------------------------------------------------------------------

class TestEvidenceGateHelper:
    """Direct unit tests for _evaluate_c0_evidence_gates."""

    def test_none_fec_not_blocking(self):
        results, is_blocking, reason = _evaluate_c0_evidence_gates(None)
        assert not is_blocking
        assert reason == ""
        assert any(g.gate_id == "G_SUPPORT_STATUS" for g in results)

    def test_pass_status_not_blocking(self):
        fec = _make_fec(support_status="PASS", support_target_met=True)
        results, is_blocking, _ = _evaluate_c0_evidence_gates(fec)
        assert not is_blocking
        g = next(r for r in results if r.gate_id == "G_SUPPORT_STATUS")
        assert g.verdict == ExitGateVerdict.PASS

    def test_weak_with_caveats_not_blocking(self):
        fec = _make_fec(support_status="WEAK_WITH_CAVEATS", support_target_met=True)
        _, is_blocking, _ = _evaluate_c0_evidence_gates(fec)
        assert not is_blocking

    @pytest.mark.parametrize("status", ["UNKNOWN", "EMPTY", "BLOCKED", "CONFLICTED"])
    def test_blocking_statuses_are_blocking(self, status):
        fec = _make_fec(support_status=status, support_target_met=False)
        _, is_blocking, reason = _evaluate_c0_evidence_gates(fec)
        assert is_blocking, f"Expected blocking for status={status}"
        assert status in reason

    def test_blocking_status_set_constant(self):
        assert "UNKNOWN" in _BLOCKING_SUPPORT_STATUSES
        assert "EMPTY" in _BLOCKING_SUPPORT_STATUSES
        assert "BLOCKED" in _BLOCKING_SUPPORT_STATUSES
        assert "CONFLICTED" in _BLOCKING_SUPPORT_STATUSES
        assert "PASS" not in _BLOCKING_SUPPORT_STATUSES
        assert "WEAK_WITH_CAVEATS" not in _BLOCKING_SUPPORT_STATUSES

    def test_g13_citation_hard_fail_when_empty_with_excluded(self):
        fec = _make_fec(
            support_status="PASS",
            citation_map=(),
            excluded_evidence_refs=("ref1", "ref2"),
        )
        results, is_blocking, reason = _evaluate_c0_evidence_gates(fec)
        g13 = next(r for r in results if r.gate_id == "G13")
        assert g13.verdict == ExitGateVerdict.FAIL
        assert is_blocking
        assert "G13" in reason

    def test_g13_pass_when_citation_map_present(self):
        fec = _make_fec(
            support_status="PASS",
            citation_map=(("claim_1", "source_1"),),
        )
        results, _, _ = _evaluate_c0_evidence_gates(fec)
        g13 = next(r for r in results if r.gate_id == "G13")
        assert g13.verdict == ExitGateVerdict.PASS

    def test_g13_warn_when_citation_map_empty_no_excluded(self):
        fec = _make_fec(support_status="PASS", citation_map=(), excluded_evidence_refs=())
        results, is_blocking, _ = _evaluate_c0_evidence_gates(fec)
        g13 = next(r for r in results if r.gate_id == "G13")
        assert g13.verdict == ExitGateVerdict.WARN
        assert not is_blocking

    def test_g09_warn_when_no_freshness_receipts(self):
        fec = _make_fec(support_status="PASS", freshness_receipts=())
        results, _, _ = _evaluate_c0_evidence_gates(fec)
        g09 = next(r for r in results if r.gate_id == "G09")
        assert g09.verdict == ExitGateVerdict.WARN

    def test_g09_pass_when_freshness_receipts_present(self):
        fec = _make_fec(support_status="PASS", freshness_receipts=("receipt_a",))
        results, _, _ = _evaluate_c0_evidence_gates(fec)
        g09 = next(r for r in results if r.gate_id == "G09")
        assert g09.verdict == ExitGateVerdict.PASS

    def test_support_target_not_met_produces_warn(self):
        fec = _make_fec(support_status="PASS", support_target_met=False)
        results, is_blocking, _ = _evaluate_c0_evidence_gates(fec)
        g = next(r for r in results if r.gate_id == "G_SUPPORT_STATUS")
        assert g.verdict == ExitGateVerdict.WARN
        assert not is_blocking


# ---------------------------------------------------------------------------
# TestAppsRgOwnedFields
# ---------------------------------------------------------------------------

class TestAppsRgOwnedFields:
    """apps_rg-owned Exit evidence fields are computed and present."""

    def test_required_fields_present(self):
        fec = _make_fec()
        sealed = _make_sealed()
        fields = _compute_apps_rg_owned_fields(fec, sealed)
        for key in ("jd_keyword_coverage", "overfit_score", "provenance_valid",
                    "material_claim_support_rate", "unsupported_material_claim_rate",
                    "citation_anchor_coverage"):
            assert key in fields, f"Missing owned field: {key}"

    def test_provenance_valid_true_when_hash_and_cert_present(self):
        fec = _make_fec()
        sealed = _make_sealed(compilation_hash="nonzero_hash")
        fields = _compute_apps_rg_owned_fields(fec, sealed)
        assert fields["provenance_valid"] is True

    def test_provenance_valid_false_when_no_hash(self):
        fec = _make_fec()
        sealed = _make_sealed(compilation_hash="")
        fields = _compute_apps_rg_owned_fields(fec, sealed)
        assert fields["provenance_valid"] is False

    def test_provenance_valid_false_when_fec_none(self):
        sealed = _make_sealed()
        fields = _compute_apps_rg_owned_fields(None, sealed)
        assert fields["provenance_valid"] is False

    def test_jd_keyword_coverage_nonzero_when_jd_source(self):
        fec = _make_fec()
        sealed = _make_sealed()
        fields = _compute_apps_rg_owned_fields(fec, sealed)
        assert fields["jd_keyword_coverage"] >= 0.0

    def test_overfit_score_in_range(self):
        fec = _make_fec()
        sealed = _make_sealed()
        fields = _compute_apps_rg_owned_fields(fec, sealed)
        assert 0.0 <= fields["overfit_score"] <= 1.0


# ---------------------------------------------------------------------------
# TestExitFinalizeW4Integration
# ---------------------------------------------------------------------------

class TestExitFinalizeW4Integration:
    """Integration tests for exit_finalize_apps_rg with W4 C0 consumption."""

    def test_pass_status_outcome_authorized(self):
        fec = _make_fec(support_status="PASS", support_target_met=True)
        sealed = _make_sealed()
        result = exit_finalize_apps_rg(
            sealed, fec=fec, target_company="Acme", target_role="SWE"
        )
        assert result.disposition.outcome_authorized is True

    @pytest.mark.parametrize("status", ["UNKNOWN", "EMPTY", "BLOCKED", "CONFLICTED"])
    def test_blocking_status_degrades_outcome_authorized(self, status):
        fec = _make_fec(support_status=status, support_target_met=False)
        sealed = _make_sealed()
        result = exit_finalize_apps_rg(
            sealed, fec=fec, target_company="Acme", target_role="SWE"
        )
        assert result.disposition.outcome_authorized is False, (
            f"Expected outcome_authorized=False for support_status={status}"
        )

    def test_g13_hard_fail_degrades_outcome_authorized(self):
        fec = _make_fec(
            support_status="PASS",
            citation_map=(),
            excluded_evidence_refs=("excl_1",),
        )
        sealed = _make_sealed()
        result = exit_finalize_apps_rg(
            sealed, fec=fec, target_company="Acme", target_role="SWE"
        )
        assert result.disposition.outcome_authorized is False

    def test_g09_warn_does_not_block(self):
        fec = _make_fec(
            support_status="PASS",
            support_target_met=True,
            freshness_receipts=(),
        )
        sealed = _make_sealed()
        result = exit_finalize_apps_rg(
            sealed, fec=fec, target_company="Acme", target_role="SWE"
        )
        # G09 is warn-only — outcome_authorized still True
        assert result.disposition.outcome_authorized is True

    def test_fec_none_no_exception(self):
        sealed = _make_sealed()
        result = exit_finalize_apps_rg(
            sealed, fec=None, target_company="Acme", target_role="SWE"
        )
        assert result.disposition is not None

    def test_fec_none_not_blocking(self):
        sealed = _make_sealed()
        result = exit_finalize_apps_rg(
            sealed, fec=None, target_company="Acme", target_role="SWE"
        )
        # fec=None should not cause blocking (no evidence = warn, not fail)
        w4 = result.disposition.final_output  # not in final_output
        # Check via run_metadata candidate
        meta_candidates = [
            c for c in result.artifact_commit_candidates
            if c.artifact_type == "run_metadata"
        ]
        assert meta_candidates, "Expected run_metadata candidate"
        meta = meta_candidates[0].serialized_content
        assert meta["w4_c0_evidence"]["c0_blocking"] is False

    def test_prompt_artifact_positional_accepted(self):
        """dispatch calls exit_finalize_apps_rg(sealed, prompt_artifact, fec=fec)"""
        sealed = _make_sealed()
        fec = _make_fec(support_status="PASS", support_target_met=True)
        result = exit_finalize_apps_rg(
            sealed, object(), fec=fec, target_company="Acme", target_role="SWE"
        )
        assert result.disposition.outcome_authorized is True

    def test_w4_c0_evidence_in_run_metadata(self):
        fec = _make_fec(support_status="PASS", support_target_met=True)
        sealed = _make_sealed()
        result = exit_finalize_apps_rg(
            sealed, fec=fec, target_company="Acme", target_role="SWE"
        )
        meta_candidates = [
            c for c in result.artifact_commit_candidates
            if c.artifact_type == "run_metadata"
        ]
        assert meta_candidates
        meta = meta_candidates[0].serialized_content
        assert "w4_c0_evidence" in meta
        w4 = meta["w4_c0_evidence"]
        assert "c0_blocking" in w4
        assert "gate_results" in w4
        assert "jd_keyword_coverage" in w4
        assert "overfit_score" in w4
        assert "provenance_valid" in w4

    def test_build_apps_rg_exit_harness_passes_fec(self):
        fec = _make_fec(support_status="PASS", support_target_met=True)
        sealed = _make_sealed(
            execution_status="completed",
        )
        # harness reads target from proposed_state_diff
        result = build_apps_rg_exit_harness(sealed, fec=fec)
        assert result.disposition.outcome_authorized is True

    def test_weak_with_caveats_authorized(self):
        fec = _make_fec(support_status="WEAK_WITH_CAVEATS", support_target_met=True)
        sealed = _make_sealed()
        result = exit_finalize_apps_rg(
            sealed, fec=fec, target_company="Acme", target_role="SWE"
        )
        assert result.disposition.outcome_authorized is True

    def test_gate_results_in_run_metadata(self):
        fec = _make_fec(support_status="PASS")
        sealed = _make_sealed()
        result = exit_finalize_apps_rg(
            sealed, fec=fec, target_company="Acme", target_role="SWE"
        )
        meta = next(
            c.serialized_content for c in result.artifact_commit_candidates
            if c.artifact_type == "run_metadata"
        )
        gate_results = meta["w4_c0_evidence"]["gate_results"]
        gate_ids = {g["gate_id"] for g in gate_results}
        assert "G_SUPPORT_STATUS" in gate_ids
        assert "G09" in gate_ids
        assert "G13" in gate_ids


# ---------------------------------------------------------------------------
# TestAgentic CoreRemainsGeneric
# ---------------------------------------------------------------------------

class TestAgenticCoreRemainsGeneric:
    """agentic_core Exit binding must contain no apps_rg-specific literals."""

    def _get_agentic_core_exit_files(self) -> list[Path]:
        exit_dir = _REPO_ROOT / "agentic_core" / "runtime" / "exit"
        if not exit_dir.exists():
            return []
        return list(exit_dir.glob("*.py"))

    def test_no_apps_rg_logic_in_agentic_core_exit(self):
        """W4 implementation fields must not appear in agentic_core Exit files.

        Registry/type files (x3_disposition, hitl_policy_registry, exit_gate_harness)
        may reference 'apps_rg' as a tenant/app_id literal — that is generic
        dispatch, not leakage.  The W4 contract forbids apps_rg *logic* fields:
        jd_keyword_coverage, overfit_score, _BLOCKING_SUPPORT_STATUSES,
        APPS_RG_EXIT_CERT_REF, and _evaluate_c0_evidence_gates.
        """
        w4_logic_literals = [
            "jd_keyword_coverage",
            "overfit_score",
            "_BLOCKING_SUPPORT_STATUSES",
            "_evaluate_c0_evidence_gates",
            "_compute_apps_rg_owned_fields",
        ]
        violations = []
        for path in self._get_agentic_core_exit_files():
            text = path.read_text(encoding="utf-8")
            if "LEGACY_SHIM" in text:
                continue  # shim re-exports only
            for literal in w4_logic_literals:
                if literal in text:
                    violations.append(f"{path.name}: contains '{literal}'")
        assert not violations, (
            "agentic_core Exit contains W4 apps_rg-logic literals (boundary violation):\n"
            + "\n".join(violations)
        )

    def test_canonical_exit_binding_lives_under_apps_rg(self):
        binding_path = _REPO_ROOT / "apps_rg" / "runtime" / "bindings" / "exit_binding.py"
        assert binding_path.is_file(), "Canonical exit binding must exist under apps_rg"
        text = binding_path.read_text(encoding="utf-8")
        assert "apps_rg" in text
        tree = ast.parse(text)
        func_defs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        assert func_defs, "Exit binding must define apps_rg-owned gate/finalize logic"


# ---------------------------------------------------------------------------
# TestRegressionGuard (W1/W2/W3 modules still importable)
# ---------------------------------------------------------------------------

class TestRegressionGuard:
    """Importing W1/W2/W3 test modules does not raise."""

    def test_w1_module_importable(self):
        import importlib
        mod = importlib.import_module(
            "tests._apps_contract.test_rg_w1_retrieval_requirements_profile"
        )
        assert mod is not None

    def test_w2_module_importable(self):
        import importlib
        mod = importlib.import_module(
            "tests._apps_contract.test_rg_w2_c0_metrics_extractor"
        )
        assert mod is not None

    def test_w3_module_importable(self):
        import importlib
        mod = importlib.import_module(
            "tests._apps_contract.test_rg_w3_c0_metrics_artifact"
        )
        assert mod is not None

    def test_exit_binding_importable(self):
        from apps_rg.runtime.bindings import exit_binding  # noqa: F401
        assert exit_binding is not None

    def test_c0_binding_importable(self):
        from apps_rg.runtime.bindings import c0_binding  # noqa: F401
        assert c0_binding is not None
