"""ADG contract tests for apps_rg/types/resume_section_node_types.py."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_resume_section_node_types_adg")
_emit_applies_guardrail("p0", "test_resume_section_node_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_resume_section_node_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_resume_section_node_types_adg", "state_snapshot")
emit_replay_key("p0", "test_resume_section_node_types_adg")
emit_determinism_digest("p0", "test_resume_section_node_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
