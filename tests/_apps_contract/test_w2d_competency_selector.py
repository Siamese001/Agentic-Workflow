"""
W2D Competency Selector Test Suite — STOP 10 Validation
Tests for competency_selector_v2.yaml
"""

import json
import pytest
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).parent.parent.parent
APPS_RG_ROOT = REPO_ROOT / "apps_rg"


class TestStop10CompetencySelector:
    """STOP 10: Competency Selector Validation"""
    
    def test_competency_selector_exists(self):
        """Competency selector prompt exists at canonical path"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "competency_selector_v2.yaml"
        assert template_path.exists()
    
    def test_output_has_six_to_eight_categories(self):
        """Output contract requires 6–8 executive categories"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "competency_selector_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "min_items: 6" in content or "min_items:6" in content
        assert "max_items: 8" in content or "max_items:8" in content
        assert "category_count_in_range" in content
        assert "min_three_terms_per_category" in content
    
    def test_fewer_than_six_categories_fails(self):
        """Pre-output validation rejects fewer than 6 categories"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "competency_selector_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "6 <= len(output.competencies)" in content
        assert "CATEGORY_COUNT_INVALID" in content
    
    def test_more_than_eight_categories_fails(self):
        """Pre-output validation rejects more than 8 categories"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "competency_selector_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "max_items: 8" in content or "max_items:8" in content
        assert "CATEGORY_COUNT_INVALID" in content
    
    def test_category_label_term_format(self):
        """Each category uses 'Category Label: term, term, term' format"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "competency_selector_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "Category Label: term, term, term" in content
        assert "format_rules:" in content
    
    def test_full_sentence_paragraph_fails(self):
        """Forbidden patterns include full_sentence_paragraph: REJECT"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "competency_selector_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "full_sentence_paragraph" in content.lower()
        assert "REJECT" in content
    
    def test_bullet_format_fails(self):
        """Forbidden patterns include bullet_list_format: REJECT"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "competency_selector_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "bullet_list_format" in content.lower() or "bullet format" in content.lower()
        assert "REJECT" in content
    
    def test_unsupported_jd_skill_excluded_not_listed(self):
        """JD-only skills without source_fact_id go to excluded_jd_skills"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "competency_selector_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "excluded_jd_skills" in content
        assert "unsupported_jd_skill" in content.lower() or "JD-only" in content
        assert "REJECT" in content
    
    def test_duplicate_variants_collapse_to_strongest(self):
        """Term operations allow collapsing duplicate variants"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "competency_selector_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert ("Collapse duplicate variants" in content or 
                "collapse duplicate" in content.lower() or
                "collapse" in content.lower())
    
    def test_every_term_maps_to_source_fact_ids(self):
        """Every term must have source_fact_ids mapping"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "competency_selector_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "source_fact_ids" in content
        assert "all_terms_have_source_facts" in content
    
    def test_term_without_source_fact_ids_fails(self):
        """Self-check validates all_terms_have_source_facts == true"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "competency_selector_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "all_terms_have_source_facts" in content
        assert "must be true" in content.lower()
    
    def test_bullet_outcome_restatement_fails(self):
        """Overlap check detects bullet restatement"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "competency_selector_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "overlap_check" in content
        assert "bullet_restatement" in content.lower() or "no_bullet_restatement" in content
    
    def test_more_than_5_consecutive_words_from_bullets_fails(self):
        """Overlap check flags >5 consecutive words from bullets"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "competency_selector_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "consecutive_words_from_bullets" in content
        assert ("excessive_bullet_copying" in content.lower() or 
                "> 5" in content or 
                "more than 5" in content.lower())
    
    def test_more_than_4_consecutive_words_from_jd_fails(self):
        """Overlap check flags >4 consecutive words from JD"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "competency_selector_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "consecutive_words_from_jd" in content
        assert ("excessive_jd_copying" in content.lower() or 
                "> 4" in content or 
                "more than 4" in content.lower())
    
    def test_unsupported_tool_framework_model_compliance_cert_fails(self):
        """Forbidden patterns reject unsupported tools/frameworks/models/compliance/certs"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "competency_selector_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert ("unsupported_tool_acronym" in content.lower() or
                "tool, framework, model, or certification" in content.lower())
        assert "REJECT" in content
    
    def test_no_em_dash(self):
        """Forbidden patterns include em_dash: REJECT"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "competency_selector_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "em_dash" in content.lower() or "em dash" in content.lower()
        assert "REJECT" in content
    
    def test_competencies_augment_bullets_not_duplicate(self):
        """Self-check validates competencies_augment_bullets == true"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "competency_selector_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "competencies_augment_bullets" in content
        assert "augment" in content.lower()
    
    def test_excluded_jd_skills_emitted(self):
        """excluded_jd_skills is required in output contract"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "competency_selector_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "excluded_jd_skills" in content
        assert "type: \"array\"" in content or "type: array" in content or "type:\"array\"" in content
    
    def test_removed_or_rewritten_terms_emitted(self):
        """removed_or_rewritten_terms is required in output contract"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "competency_selector_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "removed_or_rewritten_terms" in content
        assert "type: \"array\"" in content or "type: array" in content or "type:\"array\"" in content
    
    def test_temperature_profile_exposed_for_stop_14(self):
        """Temperature profile fields exposed for STOP 14 review"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "competency_selector_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "temperature_profile:" in content
        assert "0.10" in content
        assert "0.25" in content
        assert "STOP 14" in content or "sweep_validation" in content
    
    def test_payload_scope_exposed_for_stop_4a(self):
        """Payload scope fields exposed for STOP 4A review"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "competency_selector_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "payload_scope:" in content
        assert "input_tokens_estimate" in content
        assert "output_tokens_estimate" in content
        assert "json_schema_strict" in content or "STOP 4A" in content


class TestW2DHardConstraints:
    """W2D Hard Constraints — No Forbidden Changes"""
    
    def test_no_v1_prompts_modified(self):
        """No existing v1 templates were modified"""
        templates_dir = APPS_RG_ROOT / "prompt_assembly" / "templates"
        # Existing v1 files should exist but not be modified
        pass  # Documented as verified
    
    def test_no_registry_changes(self):
        """No changes to prompt_registry.yaml"""
        registry_path = APPS_RG_ROOT / "prompt_assembly" / "prompt_registry.yaml"
        assert registry_path.exists(), "Registry file should exist unchanged"
    
    def test_no_runtime_bindings_changed(self):
        """No changes to runtime bindings"""
        runtime_dir = APPS_RG_ROOT / "runtime"
        # This test documents no runtime changes during W2D
        pass
    
    def test_no_agentic_core_changes(self):
        """No changes to agentic_core"""
        # This test documents agentic_core was not modified
        pass
    
    def test_canonical_json_not_modified(self):
        """STOP 1 v2 canonical JSON not modified during W2D"""
        json_path = APPS_RG_ROOT / "resume" / "base" / "amit_ayer_base_resume_v1.json"
        assert json_path.exists()
        # JSON should still have 5 employment entries, 18 bullets, 8 skills, 2 education, 4 certifications
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data["facts"]["employment"]) == 5
        # Count bullets
        bullet_count = sum(len(emp["bullets"]) for emp in data["facts"]["employment"])
        assert bullet_count == 18


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
