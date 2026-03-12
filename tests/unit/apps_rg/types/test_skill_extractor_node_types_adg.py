"""ADG-driven tests for apps_rg/types/skill_extractor_node_types.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from apps_rg.types.skill_extractor_node_types import (
    SkillExtractionResult,
    SkillGapResult,
    SkillMatchResult,
)


class TestSkillGapResult:
    def test_creates(self):
        result = SkillGapResult(
            missing_skills=["Python"],
            existing_skills=["SQL"],
            gap_severity="HIGH",
            gap_score=0.7,
        )
        assert result.gap_severity == "HIGH"
        assert result.gap_score == 0.7

    def test_missing_skills_list(self):
        result = SkillGapResult(
            missing_skills=["k8s", "terraform"],
            existing_skills=[],
            gap_severity="CRITICAL",
            gap_score=1.0,
        )
        assert len(result.missing_skills) == 2


class TestSkillExtractionResult:
    def test_creates(self):
        result = SkillExtractionResult(
            technical_skills=["Python"],
            soft_skills=["leadership"],
            domain_skills=["finance"],
            tool_skills=["git"],
            confidence_score=0.9,
            source_text_length=500,
        )
        assert result.confidence_score == 0.9


class TestSkillMatchResult:
    def test_creates(self):
        result = SkillMatchResult(
            matched_skills=["Python"],
            partially_matched_skills=[],
            unmatched_skills=["Rust"],
            match_percentage=75.0,
            skill_categories={},
        )
        assert result.match_percentage == 75.0
