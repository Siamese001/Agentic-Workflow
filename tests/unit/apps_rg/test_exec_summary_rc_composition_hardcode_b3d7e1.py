"""
Unit tests for plan exec-summary-rc-composition-hardcode-b3d7e1.

Validates that the three hard-coded 'commercialization' strings have been replaced:
  RC-E: target_picture in build_executive_summary_composition_plan
  RC-F: SENTENCE_ARC_SVP_STRATEGY[2]["guidance"] (S3 brushstroke)
  RC-G: SVP_JD_EMPHASIS_THEMES
"""

from __future__ import annotations

import pytest

from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
    SENTENCE_ARC_SVP_STRATEGY,
    SVP_JD_EMPHASIS_THEMES,
)
from apps_rg.runtime.sections.executive_summary_composition import (
    build_executive_summary_composition_plan,
)


# ---------------------------------------------------------------------------
# RC-E: target_picture
# ---------------------------------------------------------------------------

class TestTargetPicture:
    """RC-E: target_picture must not contain 'commercialization'."""

    def _build_plan(self) -> dict:
        return build_executive_summary_composition_plan(
            selected_facts=[
                {"fact_id": "fact_exec_001", "claim_text": "Technology strategy executive"},
            ],
            allowed_fact_ids={"fact_exec_001"},
            target_role="SVP IT Strategy & Innovation",
            target_company="Brown & Brown",
            briefing_text="digital innovation and enterprise IT direction",
            jd_text="innovation programs, IT strategy, digital transformation",
        )

    def test_target_picture_no_commercialization(self):
        plan = self._build_plan()
        tp = plan.get("target_picture", "")
        assert "commercialization" not in tp.lower(), (
            f"target_picture must not contain 'commercialization'; got: {tp!r}"
        )

    def test_target_picture_has_digital_innovation(self):
        plan = self._build_plan()
        tp = plan.get("target_picture", "")
        assert "digital innovation" in tp.lower(), (
            f"target_picture must contain 'digital innovation'; got: {tp!r}"
        )

    def test_target_picture_present_and_nonempty(self):
        plan = self._build_plan()
        tp = plan.get("target_picture", "")
        assert tp.strip(), "target_picture must be non-empty"

    def test_target_picture_non_strategy_unchanged(self):
        """Non-strategy-executive target_picture should not be affected."""
        plan = build_executive_summary_composition_plan(
            selected_facts=[
                {"fact_id": "fact_exec_001", "claim_text": "AI platform engineering lead"},
            ],
            allowed_fact_ids={"fact_exec_001"},
            target_role="Staff Engineer AI Platform",
            target_company="Some Corp",
        )
        tp = plan.get("target_picture", "")
        assert "commercialization" not in tp.lower(), (
            f"Non-strategy target_picture also must not have 'commercialization'; got: {tp!r}"
        )


# ---------------------------------------------------------------------------
# RC-F: S3 brushstroke guidance
# ---------------------------------------------------------------------------

class TestS3BrushstrokeGuidance:
    """RC-F: SENTENCE_ARC_SVP_STRATEGY[2] S3 guidance must not contain 'commercialization'."""

    def test_s3_guidance_no_commercialization(self):
        guidance = SENTENCE_ARC_SVP_STRATEGY[2]["guidance"]
        assert "commercialization" not in guidance.lower(), (
            f"S3 guidance must not contain 'commercialization'; got: {guidance!r}"
        )

    def test_s3_guidance_has_revenue_outcomes(self):
        guidance = SENTENCE_ARC_SVP_STRATEGY[2]["guidance"]
        assert "revenue" in guidance.lower(), (
            f"S3 guidance must contain 'revenue' (platform revenue outcomes); got: {guidance!r}"
        )

    def test_s3_guidance_arc_role_unchanged(self):
        """arc_role should still be 'scale_operating_model'."""
        row = SENTENCE_ARC_SVP_STRATEGY[2]
        assert row["arc_role"] == "scale_operating_model", (
            f"S3 arc_role must be 'scale_operating_model'; got: {row['arc_role']!r}"
        )

    def test_all_arc_guidances_no_commercialization(self):
        """No arc in SENTENCE_ARC_SVP_STRATEGY should mention 'commercialization'."""
        for i, row in enumerate(SENTENCE_ARC_SVP_STRATEGY):
            g = row.get("guidance", "")
            assert "commercialization" not in g.lower(), (
                f"Arc index {i} (role={row.get('arc_role')!r}) contains 'commercialization': {g!r}"
            )


# ---------------------------------------------------------------------------
# RC-G: SVP_JD_EMPHASIS_THEMES
# ---------------------------------------------------------------------------

class TestSvpJdEmphasisThemes:
    """RC-G: SVP_JD_EMPHASIS_THEMES must not contain 'commercialization'."""

    def test_jd_emphasis_no_commercialization(self):
        for theme in SVP_JD_EMPHASIS_THEMES:
            assert "commercialization" not in theme.lower(), (
                f"SVP_JD_EMPHASIS_THEMES must not contain 'commercialization'; found in: {theme!r}"
            )

    def test_jd_emphasis_has_revenue_generation(self):
        has_revenue = any("revenue generation" in t.lower() for t in SVP_JD_EMPHASIS_THEMES)
        assert has_revenue, (
            f"SVP_JD_EMPHASIS_THEMES must contain 'revenue generation'; got: {SVP_JD_EMPHASIS_THEMES!r}"
        )

    def test_jd_emphasis_nonempty(self):
        assert len(SVP_JD_EMPHASIS_THEMES) >= 3, (
            f"SVP_JD_EMPHASIS_THEMES should have at least 3 entries; got: {len(SVP_JD_EMPHASIS_THEMES)}"
        )


# ---------------------------------------------------------------------------
# Integration: full composition plan artifact
# ---------------------------------------------------------------------------

class TestCompositionPlanArtifact:
    """Integration: build_executive_summary_composition_plan JSON must have no 'commercialization'
    in target_picture or sentence_arc guidance fields."""

    def _strategy_plan(self) -> dict:
        return build_executive_summary_composition_plan(
            selected_facts=[
                {"fact_id": "fact_exec_leadership_001", "claim_text": "Technology executive driving enterprise IT"},
                {"fact_id": "fact_engineering_platform_006", "claim_text": "$22M IP-led revenue from platform"},
                {"fact_id": "fact_governance_003", "claim_text": "40% reduction in reporting errors"},
                {"fact_id": "fact_quant_hpc_003", "claim_text": "FSA-chartered actuarial foundation"},
            ],
            allowed_fact_ids={
                "fact_exec_leadership_001",
                "fact_engineering_platform_006",
                "fact_governance_003",
                "fact_quant_hpc_003",
            },
            target_role="SVP IT Strategy & Innovation",
            target_company="Brown & Brown",
            briefing_text="digital innovation, decentralized enterprise, innovation incubation",
            jd_text="IT strategy, innovation programs, digital transformation, governance",
        )

    def test_plan_target_picture_no_commercialization(self):
        plan = self._strategy_plan()
        tp = plan.get("target_picture", "")
        assert "commercialization" not in tp.lower(), tp

    def test_plan_sentence_arc_no_commercialization(self):
        plan = self._strategy_plan()
        for row in plan.get("sentence_arc") or []:
            g = row.get("guidance", "")
            assert "commercialization" not in g.lower(), (
                f"sentence_arc row {row.get('sentence_index')} contains 'commercialization': {g!r}"
            )

    def test_plan_brushstrokes_no_commercialization(self):
        """Brushstroke guidance in plan must not mention 'commercialization'."""
        plan = self._strategy_plan()
        for bs in plan.get("brushstrokes") or []:
            g = str(bs.get("guidance", ""))
            assert "commercialization" not in g.lower(), (
                f"Brushstroke {bs.get('brushstroke_id')!r} guidance contains 'commercialization': {g!r}"
            )
