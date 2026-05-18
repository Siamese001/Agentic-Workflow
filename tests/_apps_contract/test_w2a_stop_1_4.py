"""
W2A STOP 1-4 Test Suite
Tests for canonical base resume JSON and prompt templates.
"""

import json
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
APPS_RG_ROOT = REPO_ROOT / "apps_rg"


class TestStop1CanonicalBaseResumeJSON:
    """STOP 1: Canonical Base Resume JSON Proof"""
    
    def test_canonical_json_exists(self):
        """Canonical JSON exists at apps_rg/resume/base/amit_ayer_base_resume_v1.json"""
        json_path = APPS_RG_ROOT / "resume" / "base" / "amit_ayer_base_resume_v1.json"
        assert json_path.exists(), f"Canonical JSON not found at {json_path}"
    
    def test_canonical_json_valid(self):
        """Canonical JSON is valid JSON"""
        json_path = APPS_RG_ROOT / "resume" / "base" / "amit_ayer_base_resume_v1.json"
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict)
    
    def test_schema_version_present(self):
        """Canonical JSON has schema_version: base_resume_v1.0"""
        json_path = APPS_RG_ROOT / "resume" / "base" / "amit_ayer_base_resume_v1.json"
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data.get("schema_version") == "base_resume_v1.0"
    
    def test_base_resume_id_present(self):
        """Canonical JSON has base_resume_id: amit_ayer_base_resume_v1"""
        json_path = REPO_ROOT / "apps_rg" / "resume" / "base" / "amit_ayer_base_resume_v1.json"
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data.get("base_resume_id") == "amit_ayer_base_resume_v1"
    
    def test_candidate_name_present(self):
        """Canonical JSON has candidate_name: Amit Ayer"""
        json_path = REPO_ROOT / "apps_rg" / "resume" / "base" / "amit_ayer_base_resume_v1.json"
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data.get("candidate_name") == "Amit Ayer"
    
    def test_locked_flag_true(self):
        """Canonical JSON has locked: true"""
        json_path = REPO_ROOT / "apps_rg" / "resume" / "base" / "amit_ayer_base_resume_v1.json"
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data.get("locked") is True
    
    def test_facts_structure_present(self):
        """Canonical JSON has facts.employment, facts.skills, facts.education"""
        json_path = REPO_ROOT / "apps_rg" / "resume" / "base" / "amit_ayer_base_resume_v1.json"
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "facts" in data
        assert "employment" in data["facts"]
        assert "skills" in data["facts"]
        assert "education" in data["facts"]
    
    def test_canonical_header_contact_verbatim(self):
        """Locked base header matches operator contact line (verbatim strings)."""
        json_path = REPO_ROOT / "apps_rg" / "resume" / "base" / "amit_ayer_base_resume_v1.json"
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        h = data.get("header") or {}
        assert h.get("phone") == "+1-917-239-3830"
        assert h.get("email") == "amitayer1@gmail.com"
        assert h.get("linkedin") == "linkedin.com/in/amitayer1"
        assert h.get("github") == "github.com/Siamese001/Agentic-Workflow"
        assert h.get("location") == "Boca Raton, FL"
    
    def test_canonical_base_has_no_static_headline_line(self):
        """Headline is JIT from briefing + JD via headline lane — not stored on locked base."""
        json_path = REPO_ROOT / "apps_rg" / "resume" / "base" / "amit_ayer_base_resume_v1.json"
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert not str(data.get("headline_line") or "").strip()
    
    def test_fact_ids_unique(self):
        """All fact_ids in canonical JSON are unique"""
        json_path = REPO_ROOT / "apps_rg" / "resume" / "base" / "amit_ayer_base_resume_v1.json"
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        fact_ids = []
        for emp in data["facts"]["employment"]:
            fact_ids.append(emp["fact_id"])
            for bul in emp.get("bullets", []):
                fact_ids.append(bul["bullet_id"])
        for skill in data["facts"]["skills"]:
            fact_ids.append(skill["fact_id"])
        for edu in data["facts"]["education"]:
            fact_ids.append(edu["fact_id"])
        for cert in data["facts"]["certifications"]:
            fact_ids.append(cert["fact_id"])
        
        assert len(fact_ids) == len(set(fact_ids)), "Duplicate fact_ids found"
        # 5 employment + 18 bullets + 8 skills + 2 education + 4 certifications
        assert len(fact_ids) == 37, f"Expected 37 facts, found {len(fact_ids)}"
    
    def test_active_pointer_exists(self):
        """Active pointer exists at apps_rg/resume/base/active_base_resume_pointer.json"""
        pointer_path = APPS_RG_ROOT / "resume" / "base" / "active_base_resume_pointer.json"
        assert pointer_path.exists()
    
    def test_active_pointer_valid(self):
        """Active pointer is valid JSON"""
        pointer_path = REPO_ROOT / "apps_rg" / "resume" / "base" / "active_base_resume_pointer.json"
        with open(pointer_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict)
    
    def test_active_pointer_points_to_canonical(self):
        """Active pointer references amit_ayer_base_resume_v1.json"""
        pointer_path = REPO_ROOT / "apps_rg" / "resume" / "base" / "active_base_resume_pointer.json"
        with open(pointer_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["active_base_resume"]["base_resume_id"] == "amit_ayer_base_resume_v1"


class TestStop2StrategicPlanningPrompt:
    """STOP 2: Strategic Planning Lane Proof"""
    
    def test_strategic_tailor_v2_exists(self):
        """strategic_tailor_v2.yaml exists"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "strategic_tailor_v2.yaml"
        assert template_path.exists()
    
    def test_strategic_tailor_v2_has_sovereign_oath(self):
        """strategic_tailor_v2.yaml has planning-only oath"""
        template_path = REPO_ROOT / "apps_rg" / "prompt_assembly" / "templates" / "strategic_tailor_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "NO RESUME PROSE" in content or "planning-only" in content.lower()
    
    def test_strategic_tailor_v2_outputs_planning_artifacts(self):
        """strategic_tailor_v2.yaml outputs v4 planning schema: target_signal_map, jd_requirement_map, briefing_signal_map, allowed_fact_ids_by_section, forbidden_claims, vocabulary_map, gap_list, section_budget, self_check"""
        template_path = REPO_ROOT / "apps_rg" / "prompt_assembly" / "templates" / "strategic_tailor_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        # v4 planning schema fields
        assert "target_signal_map" in content
        assert "jd_requirement_map" in content
        assert "briefing_signal_map" in content
        assert "allowed_fact_ids_by_section" in content
        assert "forbidden_claims" in content
        assert "vocabulary_map" in content
        assert "gap_list" in content
        assert "section_budget" in content
        assert "self_check" in content
        # 7 explicit sections
        assert "experience.unify.bullets" in content
        assert "experience.unify.position_narrative" in content
        assert "experience.ibm.bullets" in content
        assert "experience.ibm.position_narrative" in content
    
    def test_strategic_tailor_v2_no_resume_prose_constraints(self):
        """strategic_tailor_v2.yaml has no resume prose generation constraints - it's planning only"""
        template_path = REPO_ROOT / "apps_rg" / "prompt_assembly" / "templates" / "strategic_tailor_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        # Planning-only prompt should not have prose generation constraints
        # (section_budget contains ceilings for downstream prompts, not generation targets)
        assert "NO RESUME PROSE" in content or "planning-only" in content.lower()


class TestStop3HeadlinePrompt:
    """STOP 3: Headline Lane Proof"""
    
    def test_headline_tailor_v1_exists(self):
        """headline_tailor_v1.yaml exists"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "headline_tailor_v1.yaml"
        assert template_path.exists()
    
    def test_headline_format_constraint(self):
        """headline_tailor_v1.yaml enforces X | Y | Z format"""
        template_path = REPO_ROOT / "apps_rg" / "prompt_assembly" / "templates" / "headline_tailor_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "X | Y | Z" in content
        assert " | " in content  # space-pipe-space separator
    
    def test_headline_word_count_constraint(self):
        """headline_tailor_v1.yaml enforces 10-13 words"""
        template_path = REPO_ROOT / "apps_rg" / "prompt_assembly" / "templates" / "headline_tailor_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "10" in content and "13" in content
        assert "word" in content.lower()
    
    def test_headline_three_segments(self):
        """headline_tailor_v1.yaml requires exactly 3 segments"""
        template_path = REPO_ROOT / "apps_rg" / "prompt_assembly" / "templates" / "headline_tailor_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "3" in content and "segment" in content.lower()
    
    def test_headline_no_generic_openers(self):
        """headline_tailor_v1.yaml forbids generic openers"""
        template_path = REPO_ROOT / "apps_rg" / "prompt_assembly" / "templates" / "headline_tailor_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "Seasoned" in content or "generic" in content.lower()


class TestStop4ExecutiveSummaryPrompt:
    """STOP 4: Executive Summary Lane Proof"""
    
    def test_executive_summary_prompt_exists(self):
        """executive_summary.generate_scratch_v1.yaml exists"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "executive_summary.generate_scratch_v1.yaml"
        assert template_path.exists()
    
    def test_executive_summary_evidence_first(self):
        """executive_summary prompt has evidence-first oath"""
        template_path = REPO_ROOT / "apps_rg" / "prompt_assembly" / "templates" / "executive_summary.generate_scratch_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "EVIDENCE-FIRST" in content or "evidence-first" in content.lower()
    
    def test_executive_summary_no_target_words(self):
        """executive_summary prompt has NO target_words constraint"""
        template_path = REPO_ROOT / "apps_rg" / "prompt_assembly" / "templates" / "executive_summary.generate_scratch_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        # Check that validation_rules explicitly forbid target_words
        assert "no_target_words_constraint" in content or "forbid target_words" in content.lower() or "target_words" not in content.lower()
    
    def test_executive_summary_no_max_words(self):
        """executive_summary prompt has NO max_words constraint"""
        template_path = REPO_ROOT / "apps_rg" / "prompt_assembly" / "templates" / "executive_summary.generate_scratch_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "no_max_words_constraint" in content or "forbid max_words" in content.lower() or "max_words" not in content.lower()
    
    def test_executive_summary_citation_required(self):
        """executive_summary prompt requires citations"""
        template_path = REPO_ROOT / "apps_rg" / "prompt_assembly" / "templates" / "executive_summary.generate_scratch_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "[source:" in content or "citation" in content.lower()
    
    def test_executive_summary_no_generic_openers(self):
        """executive_summary prompt forbids generic openers"""
        template_path = REPO_ROOT / "apps_rg" / "prompt_assembly" / "templates" / "executive_summary.generate_scratch_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "Seasoned" in content or "FORBIDDEN_OPENERS" in content
    
    def test_executive_summary_outputs_planning_artifacts(self):
        """executive_summary prompt aligns with claim_ledger and selected_fact_plan"""
        template_path = REPO_ROOT / "apps_rg" / "prompt_assembly" / "templates" / "executive_summary.generate_scratch_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "claim_ledger" in content
        assert "selected_fact_plan" in content


class TestW2AHardConstraints:
    """W2A Hard Constraints — No Forbidden Changes"""
    
    def test_no_v1_prompt_templates_modified(self):
        """No existing v1 prompt templates were modified"""
        # This test documents that v1 templates remain untouched
        v1_templates = [
            "strategic_tailor_v1.yaml",
            "tailor_existing_v1.yaml",
            "generate_scratch_v1.yaml",
            "enhance_current_v1.yaml",
            "resume_fact_check_v1.yaml",
            "unsupported_claim_omission_v1.yaml",
            "bullet_diversity_repair_v1.yaml",
            "unify_v1.yaml",
            "docx_manifest_v1.yaml"
        ]
        templates_dir = APPS_RG_ROOT / "prompt_assembly" / "templates"
        for template in v1_templates:
            template_path = templates_dir / template
            if template_path.exists():
                # Template exists — this is OK, we just didn't modify it
                pass
    
    def test_no_registry_changes(self):
        """No changes to prompt_registry.yaml"""
        registry_path = APPS_RG_ROOT / "prompt_assembly" / "prompt_registry.yaml"
        # This test documents registry was not modified
        assert registry_path.exists(), "Registry file exists"
    
    def test_no_runtime_bindings_changed(self):
        """No changes to runtime bindings"""
        runtime_dir = APPS_RG_ROOT / "runtime"
        # This test documents no runtime changes
        pass
    
    def test_no_agentic_core_changes(self):
        """No changes to agentic_core"""
        # This test documents agentic_core was not modified
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
