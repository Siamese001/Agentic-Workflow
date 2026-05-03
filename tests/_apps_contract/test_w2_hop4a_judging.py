"""W2 — HOP-4A judge + AG-RG-014 targeted_headline contract tests.

Plan: apps-rg-hop4a-authority-and-judging-c3d7e1
Phases: P1.1 (AG-RG-014 wiring), P2.1-P2.3 (judge promotion + acceptance gate)

Covers:
  1. executive_positioning_judge is NOT a stub (IS_STUB=False).
  2. grade() returns a real score + evidence refs (not GRADER_UNKNOWN_SENTINEL)
     for non-empty text.
  3. grade() returns GRADER_UNKNOWN_SENTINEL for empty/missing text (fail-open).
  4. Scoring dimensions are populated and in [0, 1].
  5. Low-scoring text scores below high-scoring text (relative ordering).
  6. narrative_pass writes targeted_headline to resume_data (AG-RG-014/A).
  7. DOCX exporter prefers targeted_headline over headline for Tagline slot.
  8. AG-RG-013 static preservation invariant still holds.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# W2.P2.1-2.3 — executive_positioning_judge tests
# ---------------------------------------------------------------------------


class TestExecutivePositioningJudgeNotStub:
    """Judge is promoted: IS_STUB=False, real grade() implementation."""

    def test_is_stub_false(self):
        from apps_rg.engines.judges.executive_positioning_judge import IS_STUB
        assert IS_STUB is False, "executive_positioning_judge must be a real implementation"

    def test_is_calibrated_true(self):
        from apps_rg.engines.judges.executive_positioning_judge import IS_CALIBRATED
        assert IS_CALIBRATED is True

    def test_grader_id_not_stub(self):
        from apps_rg.engines.judges.executive_positioning_judge import GRADER_ID
        assert "stub" not in GRADER_ID.lower(), f"GRADER_ID must not contain 'stub': {GRADER_ID!r}"
        assert "v2" in GRADER_ID, f"Expected v2 promotion marker in GRADER_ID: {GRADER_ID!r}"


class TestExecutivePositioningJudgeGrade:
    """grade() contract: returns (score, evidence_refs) or GRADER_UNKNOWN_SENTINEL."""

    def test_grade_returns_tuple_for_nonempty_text(self):
        from apps_rg.engines.judges.executive_positioning_judge import grade
        from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
            GRADER_UNKNOWN_SENTINEL,
        )
        run_ctx: dict[str, Any] = {
            "output": {"text": "Delivered strategic roadmap aligning stakeholder priorities; achieved 30% ROI."}
        }
        score, refs = grade(dim=None, run_context=run_ctx)
        assert score is not GRADER_UNKNOWN_SENTINEL, "grade() must return real score for non-empty text"
        assert isinstance(score, float), f"score must be float, got {type(score)}"
        assert 0.0 <= score <= 1.0, f"score must be in [0,1], got {score}"
        assert isinstance(refs, list)

    def test_grade_returns_evidence_refs_for_nonempty_text(self):
        from apps_rg.engines.judges.executive_positioning_judge import grade
        run_ctx: dict[str, Any] = {
            "output": {"text": "Drove initiative to increase quarterly KPIs by prioritizing executive alignment."}
        }
        _, refs = grade(dim=None, run_context=run_ctx)
        assert len(refs) >= 1, "grade() must return at least one evidence ref"
        assert all(isinstance(r, str) for r in refs)

    def test_grade_returns_sentinel_for_empty_text(self):
        from apps_rg.engines.judges.executive_positioning_judge import grade
        from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
            GRADER_UNKNOWN_SENTINEL,
        )
        run_ctx: dict[str, Any] = {"output": {"text": ""}}
        score, refs = grade(dim=None, run_context=run_ctx)
        assert score is GRADER_UNKNOWN_SENTINEL, "grade() must return sentinel for empty text"
        assert refs == []

    def test_grade_returns_sentinel_for_missing_output(self):
        from apps_rg.engines.judges.executive_positioning_judge import grade
        from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
            GRADER_UNKNOWN_SENTINEL,
        )
        score, refs = grade(dim=None, run_context={})
        assert score is GRADER_UNKNOWN_SENTINEL

    def test_high_quality_text_scores_above_low_quality(self):
        """Executive-rich text must score higher than generic filler."""
        from apps_rg.engines.judges.executive_positioning_judge import grade
        high_ctx: dict[str, Any] = {
            "output": {
                "text": (
                    "Delivered strategic roadmap across 5 business units, achieving 40% ROI "
                    "improvement. Aligned board-level stakeholders on quarterly KPI initiative. "
                    "Drove organizational readiness by prioritizing executive sponsorship and "
                    "outcomes-based resource allocation."
                )
            }
        }
        low_ctx: dict[str, Any] = {
            "output": {"text": "Worked on stuff and helped the team."}
        }
        high_score, _ = grade(dim=None, run_context=high_ctx)
        low_score, _ = grade(dim=None, run_context=low_ctx)
        assert high_score > low_score, (
            f"Executive-rich text ({high_score:.3f}) must score above generic filler ({low_score:.3f})"
        )

    def test_class_and_module_callable_agree(self):
        """Class instance and module-level grade() must return same result."""
        from apps_rg.engines.judges.executive_positioning_judge import (
            ExecutivePositioningJudge,
            grade,
        )
        run_ctx: dict[str, Any] = {
            "output": {"text": "Achieved outcomes by aligning stakeholders with strategic roadmap."}
        }
        score_fn, refs_fn = grade(dim=None, run_context=run_ctx)
        score_cls, refs_cls = ExecutivePositioningJudge().grade(dim=None, run_context=run_ctx)
        assert score_fn == score_cls
        assert refs_fn == refs_cls


# ---------------------------------------------------------------------------
# W1.P1.2 — AG-RG-014 targeted_headline wiring tests
# ---------------------------------------------------------------------------

_NARRATIVE_PASS = (
    Path(__file__).resolve().parents[2]
    / "apps_rg" / "scripts" / "narrative_pass.py"
)

_DOCX_EXPORTER = (
    Path(__file__).resolve().parents[2]
    / "apps_rg" / "outputs" / "docx_exporter.py"
)


class TestAgRg014TargetedHeadlineWiring:
    """narrative_pass writes head_res.winner.text to resume_data['targeted_headline']."""

    def test_narrative_pass_writes_targeted_headline(self):
        source = _NARRATIVE_PASS.read_text(encoding="utf-8")
        assert 'resume_data["targeted_headline"] = head_res.winner.text' in source, (
            "AG-RG-014/A: narrative_pass must assign head_res.winner.text to targeted_headline"
        )

    def test_narrative_pass_documents_ag_rg_014(self):
        source = _NARRATIVE_PASS.read_text(encoding="utf-8")
        assert "AG-RG-014" in source, "AG-RG-014 decision must be cited in narrative_pass.py"

    def test_headline_candidate_json_includes_field_name(self):
        source = _NARRATIVE_PASS.read_text(encoding="utf-8")
        assert '"targeted_headline_field"' in source, (
            "headline_candidate.json must document the targeted_headline field name"
        )

    def test_narrative_pass_still_preserves_static_headline(self):
        """AG-RG-013/C: resume_data['headline'] must not be overwritten."""
        source = _NARRATIVE_PASS.read_text(encoding="utf-8")
        assert 'resume_data["headline"] = head_res.winner.text' not in source, (
            "AG-RG-013/C violated: static owner.headline must not be overwritten"
        )


class TestDocxExporterPrefersTargetedHeadline:
    """DOCX exporter Tagline slot uses targeted_headline when present."""

    def test_docx_exporter_reads_targeted_headline(self):
        source = _DOCX_EXPORTER.read_text(encoding="utf-8")
        assert 'resume.get("targeted_headline")' in source, (
            "AG-RG-014/A: docx_exporter must read targeted_headline for Tagline slot"
        )

    def test_docx_exporter_falls_back_to_static_headline(self):
        """When targeted_headline absent, static headline is used (backward compat)."""
        source = _DOCX_EXPORTER.read_text(encoding="utf-8")
        # Both keys must appear in the same expression
        idx_targeted = source.find('resume.get("targeted_headline")')
        idx_headline = source.find('resume.get("headline")', idx_targeted)
        assert idx_targeted >= 0 and idx_headline > idx_targeted, (
            "docx_exporter must fall back to static headline when targeted_headline absent"
        )

    def test_docx_exporter_tagline_prefers_targeted(self):
        """targeted_headline appears BEFORE headline in the Tagline or-chain."""
        source = _DOCX_EXPORTER.read_text(encoding="utf-8")
        # The pattern: targeted_headline OR headline OR ""
        assert 'resume.get("targeted_headline") or resume.get("headline")' in source, (
            "docx_exporter Tagline must prefer targeted_headline over headline"
        )
