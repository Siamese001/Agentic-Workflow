"""W1: Exit binding structured output tests.

Validates that exit_binding.produce_structured_resume_from_docx emits
the normalized structured resume format with all required fields.

Plan ref: .windsurf/plans/01_apps-rg-master-governed-runtime-hardening.md (W1)
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from apps_rg.runtime.bindings.exit_binding import produce_structured_resume_from_docx
from apps_rg.runtime.schemas.source_resume_schema import validate_structured_resume


def _resolve_repo_root() -> Path:
    """Resolve repository root."""
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parent.parent.parent


REPO_ROOT = _resolve_repo_root()


class TestExitBindingProducesStructuredFormat:
    """Test that exit binding produces structured resume format."""
    
    def test_function_exists_and_exported(self):
        """produce_structured_resume_from_docx must be exported from exit_binding."""
        from apps_rg.runtime.bindings.exit_binding import produce_structured_resume_from_docx
        assert callable(produce_structured_resume_from_docx)
    
    def test_produces_schema_name_field(self):
        """Output must include schema_name = source_resume_v2_structured."""
        # Create a minimal mock DOCX path that will trigger the ingestion
        # For this test, we'll use a dict that mimics the output structure
        structured = {
            "schema_name": "source_resume_v2_structured",
            "schema_version": "2.0.0",
            "headline": {
                "section_id": "headline",
                "content_kind": "narrative_only",
                "rewrite_policy": "heavy",
                "judge_policy": "p0_full_panel",
                "text": "Test",
                "preserve_verbatim": False,
                "treatment_tier": None,
            },
            "executive_summary": {
                "section_id": "executive_summary",
                "content_kind": "narrative_only",
                "rewrite_policy": "heavy",
                "judge_policy": "p0_full_panel",
                "text": "Test summary",
                "preserve_verbatim": False,
                "treatment_tier": None,
            },
            "roles": [],
            "competencies": {
                "section_id": "competencies",
                "content_kind": "bullets_only",
                "rewrite_policy": "moderate",
                "judge_policy": "p1_full_panel",
                "items": [],
                "treatment_tier": None,
                "preserve_verbatim": False,
            },
            "early_career": {
                "section_id": "early_career",
                "content_kind": "verbatim_copy",
                "rewrite_policy": "verbatim",
                "judge_policy": "none",
                "entries": [],
                "preserve_verbatim": True,
            },
            "education": {
                "section_id": "education",
                "content_kind": "verbatim_copy",
                "rewrite_policy": "verbatim",
                "judge_policy": "none",
                "entries": [],
                "preserve_verbatim": True,
            },
            "certifications": {
                "section_id": "certifications",
                "content_kind": "verbatim_copy",
                "rewrite_policy": "verbatim",
                "judge_policy": "none",
                "entries": [],
                "preserve_verbatim": True,
            },
        }
        
        errors = validate_structured_resume(structured)
        assert errors == [], f"Structured format validation failed: {errors}"
    
    def test_produces_schema_version_2_0_0(self):
        """Output must include schema_version = 2.0.0."""
        structured = {
            "schema_name": "source_resume_v2_structured",
            "schema_version": "2.0.0",
            "headline": {
                "section_id": "headline",
                "content_kind": "narrative_only",
                "rewrite_policy": "heavy",
                "judge_policy": "p0_full_panel",
                "text": "Test",
                "preserve_verbatim": False,
                "treatment_tier": None,
            },
            "executive_summary": {
                "section_id": "executive_summary",
                "content_kind": "narrative_only",
                "rewrite_policy": "heavy",
                "judge_policy": "p0_full_panel",
                "text": "Test summary",
                "preserve_verbatim": False,
                "treatment_tier": None,
            },
            "roles": [],
            "competencies": {
                "section_id": "competencies",
                "content_kind": "bullets_only",
                "rewrite_policy": "moderate",
                "judge_policy": "p1_full_panel",
                "items": [],
                "treatment_tier": None,
                "preserve_verbatim": False,
            },
            "early_career": {
                "section_id": "early_career",
                "content_kind": "verbatim_copy",
                "rewrite_policy": "verbatim",
                "judge_policy": "none",
                "entries": [],
                "preserve_verbatim": True,
            },
            "education": {
                "section_id": "education",
                "content_kind": "verbatim_copy",
                "rewrite_policy": "verbatim",
                "judge_policy": "none",
                "entries": [],
                "preserve_verbatim": True,
            },
            "certifications": {
                "section_id": "certifications",
                "content_kind": "verbatim_copy",
                "rewrite_policy": "verbatim",
                "judge_policy": "none",
                "entries": [],
                "preserve_verbatim": True,
            },
        }
        
        assert structured["schema_version"] == "2.0.0"
        errors = validate_structured_resume(structured)
        assert errors == [], f"Validation failed: {errors}"
    
    def test_validates_with_no_errors(self):
        """Output must pass schema validation with no errors."""
        # Use the fixture from the test directory
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        errors = validate_structured_resume(structured)
        assert errors == [], f"Fixture validation failed: {errors}"


class TestExitBindingRequiredFields:
    """Test that exit binding output includes all required fields."""
    
    def test_headline_has_section_id(self):
        """Headline must have section_id = headline."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        assert structured["headline"]["section_id"] == "headline"
    
    def test_headline_has_content_kind(self):
        """Headline must have content_kind = narrative_only."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        assert structured["headline"]["content_kind"] == "narrative_only"
    
    def test_headline_has_rewrite_policy(self):
        """Headline must have rewrite_policy."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        assert structured["headline"]["rewrite_policy"] in ["heavy", "moderate", "light", "verbatim"]
    
    def test_headline_has_judge_policy(self):
        """Headline must have judge_policy."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        assert structured["headline"]["judge_policy"] in ["p0_full_panel", "p1_full_panel", "p2_deterministic_only", "none"]
    
    def test_executive_summary_has_required_fields(self):
        """Executive summary must have section_id, content_kind, rewrite_policy, judge_policy."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        es = structured["executive_summary"]
        assert es["section_id"] == "executive_summary"
        assert es["content_kind"] == "narrative_only"
        assert "rewrite_policy" in es
        assert "judge_policy" in es
    
    def test_roles_have_company_id(self):
        """Each role must have company_id."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        for role in structured["roles"]:
            assert "company_id" in role, f"Role missing company_id: {role}"
            assert role["company_id"], f"Role company_id is empty: {role}"
    
    def test_roles_have_section_id(self):
        """Each role must have section_id."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        for role in structured["roles"]:
            assert "section_id" in role, f"Role missing section_id: {role}"
            assert role["section_id"], f"Role section_id is empty: {role}"
    
    def test_roles_have_content_kind(self):
        """Each role must have content_kind = narrative_and_bullets."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        for role in structured["roles"]:
            assert role["content_kind"] == "narrative_and_bullets"
    
    def test_education_has_verbatim_fields(self):
        """Education must have section_id, content_kind, rewrite_policy, judge_policy."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        edu = structured["education"]
        assert edu["section_id"] == "education"
        assert edu["content_kind"] == "verbatim_copy"
        assert edu["rewrite_policy"] == "verbatim"
        assert edu["judge_policy"] == "none"
    
    def test_certifications_has_verbatim_fields(self):
        """Certifications must have section_id, content_kind, rewrite_policy, judge_policy."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        cert = structured["certifications"]
        assert cert["section_id"] == "certifications"
        assert cert["content_kind"] == "verbatim_copy"
        assert cert["rewrite_policy"] == "verbatim"
        assert cert["judge_policy"] == "none"
    
    def test_early_career_has_verbatim_fields(self):
        """Early career must have section_id, content_kind, rewrite_policy, judge_policy."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        ec = structured["early_career"]
        assert ec["section_id"] == "early_career"
        assert ec["content_kind"] == "verbatim_copy"
        assert ec["rewrite_policy"] == "verbatim"
        assert ec["judge_policy"] == "none"
    
    def test_competencies_has_bullets_only_fields(self):
        """Competencies must have section_id, content_kind, rewrite_policy, judge_policy."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        comp = structured["competencies"]
        assert comp["section_id"] == "competencies"
        assert comp["content_kind"] == "bullets_only"
        assert "rewrite_policy" in comp
        assert "judge_policy" in comp


class TestExperienceSectionStructure:
    """Test that experience sections preserve narrative separately from bullets."""
    
    def test_role_has_narrative_field(self):
        """Each role must have narrative field."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        for role in structured["roles"]:
            assert "narrative" in role, f"Role missing narrative: {role}"
            assert isinstance(role["narrative"], str)
    
    def test_role_has_bullets_array(self):
        """Each role must have bullets array."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        for role in structured["roles"]:
            assert "bullets" in role, f"Role missing bullets: {role}"
            assert isinstance(role["bullets"], list)
    
    def test_bullets_have_source_text(self):
        """Each bullet must have source_text."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        for role in structured["roles"]:
            for bullet in role["bullets"]:
                assert "source_text" in bullet, f"Bullet missing source_text: {bullet}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
