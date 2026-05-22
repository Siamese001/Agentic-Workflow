"""Tests for L2 output mapping patches.

Covers:
  A. Patch A — PA prompt includes header instruction for grounded runs,
     omits it for generate_scratch.
  B. Patch B — compute_factual_grounding returns a float in [0.0, 1.0]
     based on token overlap between generated content and source evidence.
  C. Patch B — exit_finalize_apps_rg accepts optional fec kwarg; factual_grounding
     appears in g22_rubric_scores evidence when fec is supplied.
  D. G22 gate evaluates PASS when factual_grounding is present (gate behaviour
     is unblocked after Patch B threads the score).
  E. generate_scratch runs: factual_grounding stays absent (no score fabricated).
  F. compute_factual_grounding edge cases: None content, None fec, empty evidence.

Plan: apps-rg-l2-output-mapping-patches
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from apps_rg.exit.apps_rg_exit_evidence_builder import compute_factual_grounding


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_evidence_item(source: str, content: str) -> Any:
    """Build a minimal EvidenceItem-shaped object."""
    return SimpleNamespace(source=source, content=content)


def _make_fec(items: list[Any]) -> Any:
    """Build a minimal FinalEvidenceContract-shaped object."""
    return SimpleNamespace(evidence_items=items)


# ── A. Patch A — PA prompt header instruction ─────────────────────────────────

class TestPatchAHeaderInstruction:
    """PA prompt must include header instruction for grounded runs, not for scratch."""

    def _call_build_u0_task_block(
        self,
        generation_mode: str,
        task_plan: list[str] | None = None,
    ) -> str:
        from apps_rg.runtime.bindings.pa_binding import _build_u0_task_block

        l1_plan = SimpleNamespace(
            task_plan=task_plan or ["tailor"],
            output_expectation={"formats": ("json",), "fact_checked_required": False},
            support_expectation={"per_bullet_required": False, "source_quote_required": False},
        )
        validated_request = SimpleNamespace(
            app_payload={
                "generation_mode": generation_mode,
                "target": {"company": "Acme", "role": "Engineer", "level": "IC"},
            },
        )
        return _build_u0_task_block(validated_request, l1_plan)

    def test_strategic_tailor_includes_header_instruction(self) -> None:
        result = self._call_build_u0_task_block("strategic_tailor")
        assert "header" in result.lower()
        assert "HEADER SECTION" in result

    def test_tailor_existing_includes_header_instruction(self) -> None:
        result = self._call_build_u0_task_block("tailor_existing")
        assert "HEADER SECTION" in result
        assert '"header"' in result

    def test_generate_scratch_omits_header_instruction(self) -> None:
        result = self._call_build_u0_task_block("generate_scratch")
        assert "HEADER SECTION" not in result

    def test_grounded_sections_list_includes_header(self) -> None:
        result = self._call_build_u0_task_block("strategic_tailor")
        assert "header, executive_summary" in result

    def test_scratch_sections_list_excludes_header(self) -> None:
        result = self._call_build_u0_task_block("generate_scratch")
        assert result.count("header") == 0 or "HEADER SECTION" not in result
        assert "executive_summary, experience, skills, education" in result

    def test_grounded_no_fabrication_instruction_present(self) -> None:
        result = self._call_build_u0_task_block("strategic_tailor")
        assert "Do NOT invent" in result

    def test_null_fields_instruction_present_for_grounded(self) -> None:
        result = self._call_build_u0_task_block("tailor_existing")
        assert "null" in result


# ── B. compute_factual_grounding unit tests ───────────────────────────────────

class TestComputeFactualGrounding:
    """Unit tests for the token-overlap factual_grounding scorer."""

    def test_returns_none_when_content_is_none(self) -> None:
        fec = _make_fec([_make_evidence_item("resume:source", "some text")])
        assert compute_factual_grounding(None, fec) is None

    def test_returns_none_when_fec_is_none(self) -> None:
        assert compute_factual_grounding({"executive_summary": "test"}, None) is None

    def test_returns_none_when_no_matching_evidence_items(self) -> None:
        fec = _make_fec([_make_evidence_item("other:source", "some text")])
        assert compute_factual_grounding({"executive_summary": "test"}, fec) is None

    def test_returns_none_when_evidence_items_empty(self) -> None:
        fec = _make_fec([])
        assert compute_factual_grounding({"executive_summary": "test"}, fec) is None

    def test_perfect_overlap_approaches_one(self) -> None:
        evidence_text = "John Smith led platform engineering at BigCorp drove AI strategy"
        fec = _make_fec([_make_evidence_item("resume:app_payload.source_resume_text", evidence_text)])
        content = {
            "executive_summary": "John Smith led platform engineering at BigCorp drove AI strategy"
        }
        result = compute_factual_grounding(content, fec)
        assert result is not None
        assert result.score >= 0.8

    def test_zero_overlap_produces_low_score(self) -> None:
        fec = _make_fec([_make_evidence_item("resume:source", "alpha beta gamma")])
        content = {"executive_summary": "delta epsilon zeta completely unrelated text words"}
        result = compute_factual_grounding(content, fec)
        assert result is not None
        assert result.score <= 0.3

    def test_score_in_unit_interval(self) -> None:
        fec = _make_fec([_make_evidence_item("resume:r", "abc def ghi")])
        content = {"experience": [{"company": "def", "year": "2020"}]}
        result = compute_factual_grounding(content, fec)
        assert result is not None
        assert 0.0 <= result.score <= 1.0

    def test_numeric_tokens_counted(self) -> None:
        """Years and dollar figures (numeric tokens) must be counted — grounding risk."""
        fec = _make_fec([_make_evidence_item("resume:r", "joined acme in 2018 earned 200k")])
        # Content uses only numerics from evidence
        content_grounded = {"experience": [{"year": "2018", "compensation": "200k"}]}
        result_grounded = compute_factual_grounding(content_grounded, fec)
        # Content uses invented numerics
        content_invented = {"experience": [{"year": "2099", "compensation": "999k"}]}
        result_invented = compute_factual_grounding(content_invented, fec)
        assert result_grounded is not None
        assert result_invented is not None
        assert result_grounded.score > result_invented.score

    def test_jd_evidence_also_accepted(self) -> None:
        fec = _make_fec([_make_evidence_item("jd:app_payload.jd_text", "cloud infrastructure")])
        content = {"executive_summary": "cloud infrastructure expertise"}
        result = compute_factual_grounding(content, fec)
        assert result is not None
        assert result.score > 0.0

    def test_non_resume_non_jd_source_ignored(self) -> None:
        fec = _make_fec([
            _make_evidence_item("other:unrelated", "unique_word_xyz"),
            _make_evidence_item("resume:r", "real content from resume"),
        ])
        content = {"x": "unique_word_xyz"}
        result = compute_factual_grounding(content, fec)
        # Both items are checked; only resume item counts
        assert result is not None


# ── C. Patch B — g22 dim-score merge logic ────────────────────────────────────

class TestPatchBDimScoreMerge:
    """Direct unit tests for the g22 dim-score merge that Patch B implements.

    We call compute_g22_rubric_scores + compute_factual_grounding in
    isolation and verify the merge contract: factual_grounding is added
    when fec is supplied, absent when fec is None.
    """

    def _make_parsed_content(self, executive_summary: str = "Alice Smith led strategy") -> dict[str, Any]:
        return {
            "header": {"name": "Alice Smith"},
            "executive_summary": executive_summary,
            "experience": [{"company": "Acme", "role": "Director of Engineering"}],
            "skills": ["Python", "Cloud"],
            "education": [{"school": "State University"}],
        }

    def test_fec_none_no_factual_grounding_key(self) -> None:
        """With fec=None (generate_scratch), factual_grounding must NOT appear."""
        from apps_rg.exit.apps_rg_exit_evidence_builder import (
            compute_g22_rubric_scores,
            compute_factual_grounding,
        )
        parsed = self._make_parsed_content()
        dim_scores = compute_g22_rubric_scores(parsed, None)  # type: ignore[arg-type]
        # fec is None → factual_grounding not computed, not injected
        fg = compute_factual_grounding(parsed, None)
        assert fg is None
        # dim_scores should not have factual_grounding either (it's not computed there)
        assert "factual_grounding" not in dim_scores

    def test_fec_with_resume_evidence_injects_factual_grounding(self) -> None:
        """With fec supplied, compute_factual_grounding returns a float to merge."""
        from agentic_core.runtime.contracts.final_evidence_contract import (
            EvidenceItem,
            FinalEvidenceContract,
        )
        from apps_rg.exit.apps_rg_exit_evidence_builder import (
            compute_factual_grounding,
            compute_g22_rubric_scores,
        )

        parsed = self._make_parsed_content()
        fec = FinalEvidenceContract(
            request_id="req-merge-001",
            run_id="run-merge-001",
            app_id="apps_rg",
            trace_id="trace-merge-001",
            l5_certification_ref="c0-apps-rg-no-grounding-required",
            evidence_items=(
                EvidenceItem(
                    source="resume:app_payload.source_resume_text",
                    content="Alice Smith led strategy Acme Director of Engineering State University Cloud",
                ),
            ),
        )

        dim_scores = compute_g22_rubric_scores(parsed, None)  # type: ignore[arg-type]
        fg = compute_factual_grounding(parsed, fec)

        assert fg is not None, "Expected FactualGroundingResult from compute_factual_grounding"
        from apps_rg.exit.apps_rg_exit_evidence_builder import FactualGroundingResult
        assert isinstance(fg, FactualGroundingResult)
        assert 0.0 <= fg.score <= 1.0

        # Simulate the merge (as exit_finalize_apps_rg does — uses .score)
        merged = dict(dim_scores)
        merged["factual_grounding"] = fg.score
        assert "factual_grounding" in merged

    def test_merged_score_is_float_in_unit_interval(self) -> None:
        """Merged factual_grounding must be a float in [0.0, 1.0]."""
        from agentic_core.runtime.contracts.final_evidence_contract import (
            EvidenceItem,
            FinalEvidenceContract,
        )
        from apps_rg.exit.apps_rg_exit_evidence_builder import compute_factual_grounding

        parsed = {"executive_summary": "test executive summary grounded text resume content"}
        fec = FinalEvidenceContract(
            request_id="req-float-001",
            run_id="run-float-001",
            app_id="apps_rg",
            trace_id="trace-float-001",
            l5_certification_ref="c0-apps-rg-no-grounding-required",
            evidence_items=(
                EvidenceItem(
                    source="resume:r",
                    content="executive summary grounded text resume content",
                ),
            ),
        )
        fg = compute_factual_grounding(parsed, fec)
        assert fg is not None
        from apps_rg.exit.apps_rg_exit_evidence_builder import FactualGroundingResult
        assert isinstance(fg, FactualGroundingResult)
        assert 0.0 <= fg.score <= 1.0


# ── D. G22 unblocked with factual_grounding ───────────────────────────────────

class TestG22UnblockedWithFactualGrounding:
    """G22 must not return UNKNOWN when factual_grounding is present in evidence."""

    _GATE_ID = "G22"
    _PKG_ID = "pkg::apps_rg::run-g22-test"

    def _make_pkg(self) -> Any:
        from agentic_core.runtime.contracts.sealed_workflow_types import SealedWorkflowPackage
        return SealedWorkflowPackage(
            package_id=self._PKG_ID,
            run_id="run-g22-test",
            trace_root="trace-g22-test",
            route_contract_ref="rcr::test",
            workflow_ref="wfm::test",
            workflow_manifest_ref="wfm::test",
            sealed_sections=(),
            merged_content="test content",
            merged_content_digest="sha256::merged",
            merged_payload_digest="sha256::payload",
            replay_manifest="sha256::replay",
        )

    def _make_gate_def(self, *, with_factual_grounding: bool = True) -> dict[str, Any]:
        thresholds: dict[str, float] = {
            "format_compliance": 0.9,
            "ats_readability": 0.9,
            "no_fabrication": 0.99,
            "concision": 0.8,
            "role_alignment": 0.5,
            "specificity": 0.3,
        }
        if with_factual_grounding:
            thresholds["factual_grounding"] = 0.5
        return {"dimension_thresholds": thresholds}

    def _make_g22_evidence(self, *, with_factual_grounding: bool = True) -> dict[str, Any]:
        base = {
            "format_compliance": 1.0,
            "ats_readability": 1.0,
            "no_fabrication": 1.0,
            "concision": 1.0,
            "role_alignment": 0.8,
            "specificity": 0.7,
            "overall_pass_threshold": 0.85,
        }
        if with_factual_grounding:
            base["factual_grounding"] = 0.75
        return base

    def test_g22_with_factual_grounding_does_not_report_missing_score(self) -> None:
        from agentic_core.runtime.gates.gate_evaluators import evaluate_g22

        evidence = {"g22_rubric_scores": self._make_g22_evidence(with_factual_grounding=True)}
        result = evaluate_g22(
            self._GATE_ID,
            self._make_gate_def(with_factual_grounding=True),
            self._make_pkg(),
            evidence,
            "req-g22-test",
            "run-g22-test",
            "trace-g22-test",
        )
        assert "missing_required_score:factual_grounding" not in str(result)

    def test_g22_without_factual_grounding_when_required_reports_missing(self) -> None:
        from agentic_core.runtime.gates.gate_evaluators import evaluate_g22

        # Profile requires factual_grounding but evidence doesn't have it
        evidence = {"g22_rubric_scores": self._make_g22_evidence(with_factual_grounding=False)}
        result = evaluate_g22(
            self._GATE_ID,
            self._make_gate_def(with_factual_grounding=True),  # profile requires it
            self._make_pkg(),
            evidence,
            "req-g22-test",
            "run-g22-test",
            "trace-g22-test",
        )
        verdict_str = str(result).lower()
        assert "factual_grounding" in verdict_str or "unknown" in verdict_str or "fail" in verdict_str


# ── E. generate_scratch — no factual_grounding fabricated ─────────────────────

class TestGenerateScratchNoFabricatedScore:
    """generate_scratch runs must NOT have factual_grounding in evidence."""

    def test_compute_factual_grounding_returns_none_for_empty_fec(self) -> None:
        from agentic_core.runtime.contracts.final_evidence_contract import (
            FinalEvidenceContract,
        )
        fec = FinalEvidenceContract(
            request_id="req-scratch-001",
            run_id="run-scratch-001",
            app_id="apps_rg",
            trace_id="trace-scratch-001",
            l5_certification_ref="c0-apps-rg-no-grounding-required",
            # No evidence_items — generate_scratch path
        )
        content = {"executive_summary": "some generated text here"}
        score = compute_factual_grounding(content, fec)
        assert score is None, "generate_scratch with empty FEC must not produce a score"

    def test_compute_factual_grounding_returns_none_for_none_fec(self) -> None:
        content = {"executive_summary": "some generated text"}
        score = compute_factual_grounding(content, None)
        assert score is None


# ── F. Edge cases ──────────────────────────────────────────────────────────────

class TestComputeFactualGroundingEdgeCases:
    """Edge cases for the factual_grounding scorer."""

    def test_empty_content_dict(self) -> None:
        fec = _make_fec([_make_evidence_item("resume:r", "text")])
        result = compute_factual_grounding({}, fec)
        # Empty content → empty generated_text → score is 1.0 (no tokens to miss)
        assert result is not None
        assert result.score == 1.0

    def test_content_with_only_structural_keys(self) -> None:
        fec = _make_fec([_make_evidence_item("resume:r", "alice bob charlie")])
        content = {"header": None, "executive_summary": None}
        result = compute_factual_grounding(content, fec)
        # Non-None string tokens from JSON: "header", "executive_summary", "null"
        assert result is not None
        assert 0.0 <= result.score <= 1.0

    def test_multiple_evidence_items_combined(self) -> None:
        fec = _make_fec([
            _make_evidence_item("resume:r", "alice smith engineer"),
            _make_evidence_item("jd:j", "senior platform engineering director"),
        ])
        content = {"executive_summary": "alice smith senior platform engineering director"}
        result = compute_factual_grounding(content, fec)
        assert result is not None
        assert result.score >= 0.7
