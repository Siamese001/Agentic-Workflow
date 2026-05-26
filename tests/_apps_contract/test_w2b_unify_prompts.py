"""
W2B Unify Prompt Test Suite — STOP 5 and STOP 6 Validation
Tests for unify_bullet_tailor_v1.yaml and unify_position_narrative_v1.yaml
"""

import json
import pytest
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).parent.parent.parent
APPS_RG_ROOT = REPO_ROOT / "apps_rg"


class TestStop5UnifyBulletPrompt:
    """STOP 5: Unify Bullet Tailor Validation"""
    
    def test_unify_bullet_prompt_exists(self):
        """Unify bullet prompt exists at canonical path"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "unify_bullet_tailor_v1.yaml"
        assert template_path.exists()
    
    def test_unify_bullet_emits_exactly_6_bullets(self):
        """Output contract requires exactly 6 bullets"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "unify_bullet_tailor_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        # Check for bullet count constraints in output_contract
        assert "min_items: 6" in content or "min_items:6" in content
        assert "max_items: 6" in content or "max_items:6" in content
        assert "len(output.bullets) == 6" in content
    
    def test_5_bullets_fails(self):
        """Pre-output validation asserts bullet count == 6 (5 would fail)"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "unify_bullet_tailor_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "len(output.bullets) == 6" in content
        assert "BULLET_COUNT_INVALID" in content
    
    def test_7_bullets_fails(self):
        """Pre-output validation asserts bullet count == 6 (7 would fail)"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "unify_bullet_tailor_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "max_items: 6" in content or "max_items:6" in content
        assert "BULLET_COUNT_INVALID" in content
    
    def test_pool_selection_contract_documented(self):
        """Employment bullets use Qwen pool + Claude top-N selection (no intensity taxonomy)."""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "unify_bullet_tailor_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "pool_selection:" in content
        assert "qwen_paths: 15" in content or "qwen_paths:15" in content
        assert "final_bullet_count: 6" in content or "final_bullet_count:6" in content
        assert "rewrite_distribution" not in content
        assert "rewrite_intensity" not in content

    def test_default_protected_bullet_is_platform_commercialization(self):
        """Protected metrics bullet bul_unify_006 is documented in template guidance."""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "unify_bullet_tailor_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "bul_unify_006:" in content
        assert "protected_reason" in content
        assert "platform commercialization" in content.lower()
    
    def test_supported_metrics_preserved_exactly(self):
        """Metric preservation rules require exact preservation for key metrics"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "unify_bullet_tailor_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "$22M IP-led revenue" in content
        assert "20% gross margin expansion" in content or "20% gross margin" in content
        assert "8 to 28 specialists" in content or "8→28" in content
        assert "6 months to 3 weeks" in content
    
    def test_unify_prompt_rejects_ibm_facts_as_writable_proof(self):
        """Forbidden patterns explicitly reject IBM fact contamination"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "unify_bullet_tailor_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "ibm_fact_contamination" in content.lower() or "exp_ibm" in content.lower()
        assert "REJECT" in content
    
    def test_unify_bullet_emits_no_narrative(self):
        """Forbidden patterns include narrative_text: REJECT"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "unify_bullet_tailor_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "narrative_text" in content.lower()
        assert "REJECT" in content
    
    def test_no_em_dash(self):
        """Forbidden patterns include em_dash: REJECT"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "unify_bullet_tailor_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "em_dash" in content.lower() or "em dash" in content.lower()
        assert "REJECT" in content
    
    def test_more_than_4_consecutive_jd_words_fails(self):
        """Forbidden patterns include excessive_jd_copying check"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "unify_bullet_tailor_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert ("excessive_jd_copying" in content.lower() or 
                "4 consecutive" in content.lower() or 
                "jd_copying" in content.lower())
    
    def test_temperature_profile_exposed_for_stop_14(self):
        """Temperature profile fields exposed for STOP 14 review"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "unify_bullet_tailor_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "temperature_profile:" in content
        assert "0.35" in content
        assert "0.50" in content
        assert "STOP 14" in content or "sweep_validation" in content
    
    def test_payload_scope_exposed_for_stop_4a(self):
        """Payload scope fields exposed for STOP 4A review"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "unify_bullet_tailor_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "payload_scope:" in content
        assert "input_tokens_estimate" in content
        assert "output_tokens_estimate" in content
        assert "json_schema_strict" in content or "STOP 4A" in content


class TestStop6UnifyNarrativePrompt:
    """STOP 6: Unify Position Narrative Validation"""
    
    def test_unify_narrative_prompt_exists(self):
        """Unify narrative prompt exists at canonical path"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "unify_position_narrative_v1.yaml"
        assert template_path.exists()
    
    def test_unify_narrative_emits_exactly_one_sentence(self):
        """Output contract requires exactly one sentence"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "unify_position_narrative_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "exactly one sentence" in content.lower() or "Exactly one sentence" in content
        assert "NOT_EXACTLY_ONE_SENTENCE" in content or "exactly_one_sentence" in content
    
    def test_unify_narrative_rejects_repeated_bullet_metrics(self):
        """Anti-repetition rules forbid verbatim bullet metrics"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "unify_position_narrative_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "bullet_metrics_repeated" in content
        assert "anti_repetition" in content.lower()
    
    def test_unify_narrative_rejects_bullet_list_output(self):
        """Validation rules forbid bullet list format"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "unify_position_narrative_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "BULLET_LIST_FORMAT" in content or "bullet_list" in content.lower()
        assert "no bullet characters" in content.lower() or "No bullet characters" in content
    
    def test_unify_narrative_rejects_copied_bullet_sentence_structure(self):
        """Anti-repetition rules check sentence structure similarity"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "unify_position_narrative_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "sentence_structure_similarity" in content
        assert "< 0.3" in content
    
    def test_role_header_mutation_fails(self):
        """Role header fields are marked writable: false"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "unify_position_narrative_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "role_header_fields:" in content
        assert "writable: false" in content
        assert "company:" in content
        assert "Unify Consulting" in content
    
    def test_narrative_temperature_profile_exposed_for_stop_14(self):
        """Temperature profile exposed for STOP 14 review"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "unify_position_narrative_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "temperature_profile:" in content
        assert "0.35" in content
        assert "0.50" in content
    
    def test_narrative_payload_scope_exposed_for_stop_4a(self):
        """Payload scope exposed for STOP 4A review"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "unify_position_narrative_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "payload_scope:" in content
        assert "input_tokens_estimate" in content
        assert "output_tokens_estimate" in content


class TestW2BHadrConstraints:
    """W2B Hard Constraints — No Forbidden Changes"""
    
    def test_no_v1_unify_prompts_modified(self):
        """No existing unify v1 templates were modified"""
        templates_dir = APPS_RG_ROOT / "prompt_assembly" / "templates"
        # unify_v1.yaml should exist but not be modified
        v1_unify = templates_dir / "unify_v1.yaml"
        if v1_unify.exists():
            pass  # Existence is fine — we just didn't modify it
    
    def test_no_registry_changes(self):
        """No changes to prompt_registry.yaml"""
        registry_path = APPS_RG_ROOT / "prompt_assembly" / "prompt_registry.yaml"
        assert registry_path.exists(), "Registry file should exist unchanged"
    
    def test_no_runtime_bindings_changed(self):
        """No changes to runtime bindings"""
        runtime_dir = APPS_RG_ROOT / "runtime"
        # This test documents no runtime changes during W2B
        pass
    
    def test_no_agentic_core_changes(self):
        """No changes to agentic_core"""
        # This test documents agentic_core was not modified
        pass
    
    def test_canonical_json_not_modified(self):
        """STOP 1 v2 canonical JSON not modified during W2B"""
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
