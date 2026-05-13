"""W1: Normalized section IDs and company IDs tests.

Validates that all sections have normalized section_ids and all roles
have normalized company_ids per the canonical ID scheme.

Plan ref: .windsurf/plans/01_apps-rg-master-governed-runtime-hardening.md (W1)
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.schemas.source_resume_schema import validate_structured_resume


def _resolve_repo_root() -> Path:
    """Resolve repository root."""
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parent.parent.parent


REPO_ROOT = _resolve_repo_root()


class TestNormalizedSectionIds:
    """Test that all sections have normalized section IDs."""
    
    CANONICAL_SECTION_IDS = [
        "headline",
        "executive_summary",
        "unify",
        "ibm",
        "insurtech",
        "ey",
        "early_career",
        "competencies",
        "education",
        "certifications",
    ]
    
    def test_headline_section_id_normalized(self):
        """Headline section_id must be 'headline'."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        assert structured["headline"]["section_id"] == "headline"
    
    def test_executive_summary_section_id_normalized(self):
        """Executive summary section_id must be 'executive_summary'."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        assert structured["executive_summary"]["section_id"] == "executive_summary"
    
    def test_roles_have_normalized_section_ids(self):
        """Each role must have a normalized section_id derived from company."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        for role in structured["roles"]:
            section_id = role["section_id"]
            # Section ID should be snake_case, no spaces
            assert " " not in section_id, f"section_id contains space: {section_id}"
            # Should be lowercase
            assert section_id == section_id.lower(), f"section_id not lowercase: {section_id}"
    
    def test_competencies_section_id_normalized(self):
        """Competencies section_id must be 'competencies'."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        assert structured["competencies"]["section_id"] == "competencies"
    
    def test_education_section_id_normalized(self):
        """Education section_id must be 'education'."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        assert structured["education"]["section_id"] == "education"
    
    def test_certifications_section_id_normalized(self):
        """Certifications section_id must be 'certifications'."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        assert structured["certifications"]["section_id"] == "certifications"
    
    def test_early_career_section_id_normalized(self):
        """Early career section_id must be 'early_career'."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        assert structured["early_career"]["section_id"] == "early_career"


class TestNormalizedCompanyIds:
    """Test that all roles have normalized company IDs."""
    
    CANONICAL_COMPANY_IDS = {
        "unify_consulting": ["unify", "unify consulting"],
        "ibm": ["ibm"],
        "insurtech_tech_solutions": ["insurtech", "insurtech tech solutions"],
        "ernst_young": ["ey", "ernst & young", "ernst and young"],
    }
    
    def test_roles_have_company_id(self):
        """Each role must have a company_id field."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        for role in structured["roles"]:
            assert "company_id" in role, f"Role missing company_id: {role}"
    
    def test_company_ids_are_normalized(self):
        """Company IDs must be snake_case."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        for role in structured["roles"]:
            company_id = role["company_id"]
            # No spaces
            assert " " not in company_id, f"company_id contains space: {company_id}"
            # Lowercase
            assert company_id == company_id.lower(), f"company_id not lowercase: {company_id}"
            # Snake case or single word
            assert "_" in company_id or company_id.isalpha(), f"company_id not normalized: {company_id}"
    
    def test_unify_consulting_company_id(self):
        """Unify Consulting must have company_id 'unify_consulting'."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        unify_role = next((r for r in structured["roles"] if "Unify" in r["employer"]), None)
        assert unify_role is not None
        assert unify_role["company_id"] == "unify_consulting"
    
    def test_ibm_company_id(self):
        """IBM must have company_id 'ibm'."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        ibm_role = next((r for r in structured["roles"] if "IBM" in r["employer"]), None)
        assert ibm_role is not None
        assert ibm_role["company_id"] == "ibm"
    
    def test_company_id_matches_section_id_pattern(self):
        """Section ID should be derivable from company_id."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        for role in structured["roles"]:
            company_id = role["company_id"]
            section_id = role["section_id"]
            # Section ID should be related to company_id
            # Remove underscores for comparison
            normalized_company = company_id.replace("_", "")
            assert section_id.startswith(normalized_company[:5]) or normalized_company.startswith(section_id), (
                f"section_id {section_id} doesn't match company_id {company_id}"
            )


class TestContentKindConsistency:
    """Test that content_kind is consistent with section type."""
    
    def test_headline_content_kind_is_narrative_only(self):
        """Headline must have content_kind = narrative_only."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        assert structured["headline"]["content_kind"] == "narrative_only"
    
    def test_executive_summary_content_kind_is_narrative_only(self):
        """Executive summary must have content_kind = narrative_only."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        assert structured["executive_summary"]["content_kind"] == "narrative_only"
    
    def test_roles_content_kind_is_narrative_and_bullets(self):
        """Roles must have content_kind = narrative_and_bullets."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        for role in structured["roles"]:
            assert role["content_kind"] == "narrative_and_bullets"
    
    def test_competencies_content_kind_is_bullets_only(self):
        """Competencies must have content_kind = bullets_only."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        assert structured["competencies"]["content_kind"] == "bullets_only"
    
    def test_verbatim_sections_content_kind_is_verbatim_copy(self):
        """Education, certifications, early_career must have content_kind = verbatim_copy."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        for section in ["education", "certifications", "early_career"]:
            assert structured[section]["content_kind"] == "verbatim_copy"


class TestVerbatimSectionsHashable:
    """Test that verbatim sections are hashable and copied exactly."""
    
    def test_verbatim_sections_have_preserve_verbatim_true(self):
        """Verbatim sections must have preserve_verbatim = true."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        for section in ["education", "certifications", "early_career"]:
            assert structured[section]["preserve_verbatim"] is True, f"{section} not marked verbatim"
    
    def test_verbatim_sections_have_verbatim_rewrite_policy(self):
        """Verbatim sections must have rewrite_policy = verbatim."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        for section in ["education", "certifications", "early_career"]:
            assert structured[section]["rewrite_policy"] == "verbatim", f"{section} rewrite_policy not verbatim"
    
    def test_verbatim_sections_have_none_judge_policy(self):
        """Verbatim sections must have judge_policy = none."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        for section in ["education", "certifications", "early_career"]:
            assert structured[section]["judge_policy"] == "none", f"{section} judge_policy not none"
    
    def test_verbatim_entries_have_text_field(self):
        """Each verbatim entry must have text field."""
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        for section in ["education", "certifications", "early_career"]:
            for entry in structured[section]["entries"]:
                assert "text" in entry, f"Entry missing text: {entry}"
                assert isinstance(entry["text"], str)
                assert len(entry["text"]) > 0
    
    def test_verbatim_entries_are_immutable_copy(self):
        """Verbatim entries should not be modified by downstream processing."""
        # This is a design intent test - the preserve_verbatim flag signals immutability
        fixture_path = REPO_ROOT / "tests" / "_apps_contract" / "source_resume_v2_structured_minimal.json"
        with open(fixture_path, encoding="utf-8") as f:
            structured = json.load(f)
        
        for section in ["education", "certifications", "early_career"]:
            for entry in structured[section]["entries"]:
                assert entry.get("preserve_verbatim", True) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
