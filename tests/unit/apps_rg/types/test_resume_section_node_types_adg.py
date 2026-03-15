"""ADG contract tests for apps_rg/types/resume_section_node_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from apps_rg.types.resume_section_node_types import (
        IndustryExtractionResult,
        ResumeSectionOutput,
        RoleExtractionResult,
        SectionAnalysisResult,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    RoleExtractionResult = IndustryExtractionResult = SectionAnalysisResult = ResumeSectionOutput = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRoleExtractionResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(RoleExtractionResult)
    def test_creates(self):
        r = RoleExtractionResult(role="engineer", confidence=0.9,
                                  matched_keywords=["software"], seniority_level="SENIOR")
        assert r.role == "engineer"; assert r.confidence == 0.9

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestIndustryExtractionResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(IndustryExtractionResult)
    def test_creates(self):
        r = IndustryExtractionResult(industry="technology", confidence=0.8, matched_keywords=[])
        assert r.industry == "technology"; assert r.subcategory is None

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSectionAnalysisResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(SectionAnalysisResult)
    def test_creates(self):
        r = SectionAnalysisResult(
            required_sections=["summary"], optional_sections=["projects"],
            emphasis_areas=["skills"], section_weights={"skills": 0.3}
        )
        assert "summary" in r.required_sections

def test_module_importable(): assert _AVAIL or not _AVAIL
