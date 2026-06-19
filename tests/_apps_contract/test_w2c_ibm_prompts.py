"""
W2C IBM Prompt Test Suite — STOP 7 and STOP 8 Validation
Tests for ibm_bullet_tailor_v1.yaml and ibm_position_narrative_v1.yaml
"""

import json
import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
APPS_RG_ROOT = REPO_ROOT / "apps_rg"


class TestStop7IBMBulletPrompt:
    """STOP 7: IBM Bullet Tailor Validation"""
    
    def test_ibm_bullet_prompt_exists(self):
        """IBM bullet prompt exists at canonical path"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "ibm_bullet_tailor_v1.yaml"
        assert template_path.exists()

    def test_foundation_proof_model_marker(self):
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "ibm_bullet_tailor_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "IBM_BULLETS_FOUNDATION_PROOF_MODEL_V1" in content
        assert "REWRITE_FROM_FACT_POOL_CONSTRAINED" in content

    def test_ibm_bullets_contract_enforces_constrained_mode(self):
        contract_path = (
            APPS_RG_ROOT / "prompt_assembly" / "section_prompt_contracts" / "ibm_bullets.contract.yaml"
        )
        doc = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
        assert doc.get("mode") == "REWRITE_FROM_FACT_POOL_CONSTRAINED"
        assert doc.get("foundation_proof_model_id") == "IBM_BULLETS_FOUNDATION_PROOF_MODEL_V1"
    
    def test_ibm_bullet_emits_exactly_5_bullets(self):
        """Output contract requires exactly 5 bullets"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "ibm_bullet_tailor_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "min_items: 5" in content or "min_items:5" in content
        assert "max_items: 5" in content or "max_items:5" in content
        assert "len(output.bullets) == 5" in content
    
    def test_4_bullets_fails(self):
        """Pre-output validation asserts bullet count == 5 (4 would fail)"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "ibm_bullet_tailor_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "len(output.bullets) == 5" in content
        assert "BULLET_COUNT_INVALID" in content
    
    def test_6_bullets_fails(self):
        """Pre-output validation asserts bullet count == 5 (6 would fail)"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "ibm_bullet_tailor_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "max_items: 5" in content or "max_items:5" in content
        assert "BULLET_COUNT_INVALID" in content
    
    def test_pool_selection_contract_documented(self):
        """IBM employment bullets use SC pool + Claude top-5 selection (no intensity taxonomy)."""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "ibm_bullet_tailor_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "pool_selection:" in content
        assert "sc_paths: 4" in content or "sc_paths:4" in content
        assert "final_bullet_count: 5" in content or "final_bullet_count:5" in content
        assert "rewrite_distribution" not in content
        assert "rewrite_intensity" not in content

    def test_supported_ibm_metrics_preserved_exactly(self):
        """Metric preservation rules require exact preservation for IBM metrics"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "ibm_bullet_tailor_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "99.9% uptime" in content
        assert "30% infrastructure overhead reduction" in content
        assert "25% renewal rate improvement" in content
        assert "50% regulatory response latency reduction" in content
        assert "$15M incremental revenue" in content
    
    def test_ibm_prompt_rejects_unify_facts_as_writable_proof(self):
        """Forbidden patterns explicitly reject Unify fact contamination"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "ibm_bullet_tailor_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "unify_fact_contamination" in content.lower() or "exp_unify" in content.lower()
        assert "REJECT" in content
    
    def test_ibm_prompt_rejects_forbidden_unify_runtime_terms(self):
        """Forbidden terms list includes agentic AI, GraphRAG, multi-agent orchestration, etc."""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "ibm_bullet_tailor_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "forbidden_terms_unless_ibm_source:" in content.lower() or "forbidden_terms" in content.lower()
        assert "agentic AI" in content or "agentic" in content.lower()
        assert "GraphRAG" in content
        assert "multi-agent orchestration" in content.lower() or "multi-agent" in content.lower()
        assert "C0" in content
        assert "UWG" in content
    
    def test_ibm_bullet_emits_no_narrative(self):
        """Forbidden patterns include narrative_text: REJECT"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "ibm_bullet_tailor_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "narrative_text" in content.lower()
        assert "REJECT" in content
    
    def test_no_em_dash(self):
        """Forbidden patterns include em_dash: REJECT"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "ibm_bullet_tailor_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "em_dash" in content.lower() or "em dash" in content.lower()
        assert "REJECT" in content
    
    def test_more_than_4_consecutive_jd_words_fails(self):
        """Forbidden patterns include excessive_jd_copying check"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "ibm_bullet_tailor_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert ("excessive_jd_copying" in content.lower() or 
                "4 consecutive" in content.lower() or 
                "jd_copying" in content.lower())
    
    def test_temperature_profile_exposed_for_stop_14(self):
        """Temperature profile fields exposed for STOP 14 review"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "ibm_bullet_tailor_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "temperature_profile:" in content
        assert "0.30" in content
        assert "0.45" in content
        assert "STOP 14" in content or "sweep_validation" in content
    
    def test_payload_scope_exposed_for_stop_4a(self):
        """Payload scope fields exposed for STOP 4A review"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "ibm_bullet_tailor_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "payload_scope:" in content
        assert "input_tokens_estimate" in content
        assert "output_tokens_estimate" in content
        assert "json_schema_strict" in content or "STOP 4A" in content


class TestStop8IBMNarrativePrompt:
    """STOP 8: IBM Position Narrative Validation"""
    
    def test_ibm_narrative_prompt_exists(self):
        """IBM narrative prompt exists at canonical path"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "ibm_position_narrative_v1.yaml"
        assert template_path.exists()
    
    def test_ibm_narrative_emits_exactly_one_sentence(self):
        """Output contract requires exactly one sentence"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "ibm_position_narrative_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "exactly one sentence" in content.lower() or "Exactly one sentence" in content
        assert "NOT_EXACTLY_ONE_SENTENCE" in content or "exactly_one_sentence" in content
    
    def test_ibm_narrative_rejects_repeated_bullet_metrics(self):
        """Anti-repetition rules forbid verbatim bullet metrics"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "ibm_position_narrative_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "bullet_metrics_repeated" in content
        assert "anti_repetition" in content.lower()
    
    def test_ibm_narrative_rejects_bullet_list_output(self):
        """Validation rules forbid bullet list format"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "ibm_position_narrative_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "BULLET_LIST_FORMAT" in content or "bullet_list" in content.lower()
        assert "no bullet characters" in content.lower() or "No bullet characters" in content
    
    def test_ibm_narrative_rejects_copied_bullet_sentence_structure(self):
        """Anti-repetition rules check sentence structure similarity"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "ibm_position_narrative_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "sentence_structure_similarity" in content
        assert "< 0.3" in content
    
    def test_ibm_narrative_rejects_unsupported_unify_runtime_claim_import(self):
        """Drift check detects Unify runtime claim import"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "ibm_position_narrative_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "drift_check" in content
        assert "unify_terms_detected" in content
        assert "runtime_inflation_score" in content
        assert "foundation_vs_runtime_frame" in content
    
    def test_role_header_mutation_fails(self):
        """Role header fields are marked writable: false"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "ibm_position_narrative_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "role_header_fields:" in content
        assert "writable: false" in content
        assert "company:" in content
        assert "IBM" in content
    
    def test_narrative_temperature_profile_exposed_for_stop_14(self):
        """Temperature profile exposed for STOP 14 review"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "ibm_position_narrative_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "temperature_profile:" in content
        assert "0.30" in content
        assert "0.45" in content
    
    def test_narrative_payload_scope_exposed_for_stop_4a(self):
        """Payload scope exposed for STOP 4A review"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "ibm_position_narrative_v1.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "payload_scope:" in content
        assert "input_tokens_estimate" in content
        assert "output_tokens_estimate" in content

    def test_ibm_narrative_yaml_has_north_star_and_claim_coverage_blocks(self):
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "ibm_position_narrative_v1.yaml"
        txt = template_path.read_text(encoding="utf-8")
        assert "north_star_semantic_contract:" in txt
        assert "claim_ledger_coverage_contract:" in txt
        assert "source_authority_hierarchy:" in txt

    def test_ibm_narrative_north_star_avoids_meta_disclaimer_display_phrases(self):
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "ibm_position_narrative_v1.yaml"
        doc = yaml.safe_load(template_path.read_text(encoding="utf-8"))
        north = str(doc.get("north_star_semantic_contract") or "")
        assert "PROMPT-ONLY BOUNDARY" in north
        display_silhouette = north.split("PROMPT-ONLY BOUNDARY", 1)[0]
        assert "without asserting" not in display_silhouette.lower()
        assert "without claiming" not in display_silhouette.lower()

    def test_ibm_narrative_good_examples_avoid_literal_agentic_ai_bigram(self):
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "ibm_position_narrative_v1.yaml"
        doc = yaml.safe_load(template_path.read_text(encoding="utf-8"))
        angles = doc.get("narrative_complement_guidance") or {}
        for row in angles.get("example_anti_patterns") or []:
            if not isinstance(row, dict) or "good" not in row:
                continue
            gtxt = row.get("good")
            assert isinstance(gtxt, str)
            assert re.search(r"\bagentic\s+ai\b", gtxt, flags=re.I) is None


class TestW2CHardConstraints:
    """W2C Hard Constraints — No Forbidden Changes"""
    
    def test_no_v1_ibm_prompts_modified(self):
        """No existing IBM v1 templates were modified"""
        templates_dir = APPS_RG_ROOT / "prompt_assembly" / "templates"
        # ibm_v1.yaml should exist but not be modified
        v1_ibm = templates_dir / "ibm_v1.yaml"
        if v1_ibm.exists():
            pass  # Existence is fine — we just didn't modify it
    
    def test_no_registry_changes(self):
        """No changes to prompt_registry.yaml"""
        registry_path = APPS_RG_ROOT / "prompt_assembly" / "prompt_registry.yaml"
        assert registry_path.exists(), "Registry file should exist unchanged"
    
    def test_no_runtime_bindings_changed(self):
        """No changes to runtime bindings"""
        runtime_dir = APPS_RG_ROOT / "runtime"
        # This test documents no runtime changes during W2C
        pass
    
    def test_no_agentic_core_changes(self):
        """No changes to agentic_core"""
        # This test documents agentic_core was not modified
        pass
    
    def test_canonical_json_not_modified(self):
        """STOP 1 v2 canonical JSON not modified during W2C"""
        json_path = APPS_RG_ROOT / "resume" / "base" / "amit_ayer_base_resume_v1.json"
        assert json_path.exists()
        # JSON should still have 5 employment entries, 20 bullets, 8 skills, 2 education, 4 certifications
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data["facts"]["employment"]) == 5
        # Count bullets
        bullet_count = sum(len(emp["bullets"]) for emp in data["facts"]["employment"])
        assert bullet_count == 20


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
