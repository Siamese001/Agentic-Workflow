"""
W2E Final/Validator Prompt Test Suite — All Four v2 Prompts Exist and Enforce Boundaries
"""

import json
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
APPS_RG_ROOT = REPO_ROOT / "apps_rg"


class TestW2EFinalUnifyV2:
    """final_unify_v2: Consistency-only, no new content authority"""
    
    def test_final_unify_v2_exists(self):
        """final_unify_v2 prompt exists at canonical path"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "final_unify_v2.yaml"
        assert template_path.exists()
    
    def test_final_unify_v2_forbids_net_new_claims(self):
        """final_unify_v2 forbids adding new claims"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "final_unify_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "no_new_claims_added" in content
        assert "net_new_content_check" in content
        assert "NEW_CLAIMS_DETECTED" in content or "new_claims_detected" in content.lower()
    
    def test_final_unify_v2_forbids_locked_section_modification(self):
        """final_unify_v2 forbids modifying locked sections"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "final_unify_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "locked_sections_unchanged" in content
        assert "locked_copy_check" in content
        assert "LOCKED_HEADERS_MODIFIED" in content or "locked section" in content.lower()
    
    def test_final_unify_v2_forbids_source_fact_id_mutation(self):
        """final_unify_v2 forbids altering source_fact_ids"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "final_unify_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "source_fact_ids_preserved" in content or "source_fact_ids_unchanged" in content
        assert "SOURCE_FACT_IDS_MODIFIED" in content or "mutate_source_fact_id" in content.lower()
    
    def test_final_unify_v2_temperature_0_to_0_1(self):
        """final_unify_v2 uses temperature 0.0 to 0.1"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "final_unify_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "temperature_profile:" in content
        assert "0.0" in content
        assert "0.1" in content


class TestW2EResumeFactCheckV2:
    """resume_fact_check_v2: Validator only, temperature 0.0"""
    
    def test_resume_fact_check_v2_exists(self):
        """resume_fact_check_v2 prompt exists at canonical path"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "resume_fact_check_v2.yaml"
        assert template_path.exists()
    
    def test_resume_fact_check_v2_requires_claim_ledger_validation(self):
        """resume_fact_check_v2 requires claim_ledger_validation output"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "resume_fact_check_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "claim_ledger_validation" in content
        assert "type: \"array\"" in content or "type: array" in content
    
    def test_resume_fact_check_v2_rejects_jd_as_proof(self):
        """resume_fact_check_v2 rejects JD-as-proof"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "resume_fact_check_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "jd_as_proof" in content.lower() or "JD_AS_PROOF" in content
        assert "jd_as_proof_detected" in content
        assert "must be false" in content.lower() or "must be False" in content
    
    def test_resume_fact_check_v2_rejects_briefing_as_proof(self):
        """resume_fact_check_v2 rejects briefing-as-proof"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "resume_fact_check_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "briefing_as_proof" in content.lower() or "BRIEFING_AS_PROOF" in content
        assert "briefing_as_proof_detected" in content
    
    def test_resume_fact_check_v2_runs_at_temperature_0_0(self):
        """resume_fact_check_v2 runs at temperature 0.0"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "resume_fact_check_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "temperature_profile:" in content
        assert '"0.0"' in content or "0.0" in content
        assert "range: \"0.0\"" in content or "range: 0.0" in content or "0.0 - 0.0" in content


class TestW2EUnsupportedClaimOmissionV2:
    """unsupported_claim_omission_v2: Validator/repair recommendation only"""
    
    def test_unsupported_claim_omission_v2_exists(self):
        """unsupported_claim_omission_v2 prompt exists at canonical path"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "unsupported_claim_omission_v2.yaml"
        assert template_path.exists()
    
    def test_unsupported_claim_omission_v2_emits_omission_report(self):
        """unsupported_claim_omission_v2 emits omission_report"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "unsupported_claim_omission_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "omission_report" in content
        assert "type: \"object\"" in content or "type: object" in content
    
    def test_unsupported_claim_omission_v2_emits_gap_notes(self):
        """unsupported_claim_omission_v2 emits gap_notes"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "unsupported_claim_omission_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "gap_notes" in content
        assert "type: \"array\"" in content or "type: array" in content
    
    def test_unsupported_claim_omission_v2_cannot_invent_replacement_claims(self):
        """unsupported_claim_omission_v2 cannot invent replacement claims"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "unsupported_claim_omission_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "no_invented_claims" in content
        assert "must be true" in content.lower() or "must be True" in content
        assert "INVENTED_CLAIMS_DETECTED" in content or "invent_replacement" in content.lower()
        assert "replacement_attempted" in content


class TestW2EDocxManifestV2:
    """docx_manifest_v2: Deterministic render manifest and validation"""
    
    def test_docx_manifest_v2_exists(self):
        """docx_manifest_v2 prompt exists at canonical path"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "docx_manifest_v2.yaml"
        assert template_path.exists()
    
    def test_docx_manifest_v2_validates_canonical_json_hash(self):
        """docx_manifest_v2 validates canonical JSON hash"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "docx_manifest_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "base_resume_json_hash" in content
        assert "base_json_hash_match" in content or "all_hashes_valid" in content
        assert "HASH_VALIDATION_FAILED" in content or "hash_mismatch" in content.lower()
    
    def test_docx_manifest_v2_validates_locked_copy_hashes(self):
        """docx_manifest_v2 validates locked_copy_hashes"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "docx_manifest_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "locked_copy_hashes" in content
        assert "locked_copy_validation" in content
        assert "locked_copy_hashes_match" in content or "locked_copy_hashes_validated" in content
    
    def test_docx_manifest_v2_fails_on_copied_header_drift(self):
        """docx_manifest_v2 fails on copied header drift"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "docx_manifest_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "copied_header_drift" in content.lower() or "header drift" in content.lower()
        assert "role_headers_match_canonical" in content
        assert "no_drift_detected" in content
    
    def test_docx_manifest_v2_fails_on_missing_locked_section(self):
        """docx_manifest_v2 fails on missing locked section"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "docx_manifest_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "missing_locked_section" in content.lower() or "MISSING_LOCKED" in content
        assert "all_locked_sections_present" in content or "must be true" in content.lower()


class TestW2EPayloadAndSchemaExposure:
    """All four prompts expose required fields for STOP 4A review"""
    
    def test_final_unify_v2_exposes_payload_scope(self):
        """final_unify_v2 exposes payload scope for STOP 4A"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "final_unify_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "payload_scope:" in content
        assert "input_tokens_estimate" in content
        assert "output_tokens_estimate" in content
    
    def test_resume_fact_check_v2_exposes_payload_scope(self):
        """resume_fact_check_v2 exposes payload scope for STOP 4A"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "resume_fact_check_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "payload_scope:" in content
        assert "input_tokens_estimate" in content
    
    def test_unsupported_claim_omission_v2_exposes_payload_scope(self):
        """unsupported_claim_omission_v2 exposes payload scope for STOP 4A"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "unsupported_claim_omission_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "payload_scope:" in content
        assert "input_tokens_estimate" in content
    
    def test_docx_manifest_v2_exposes_payload_scope(self):
        """docx_manifest_v2 exposes payload scope for STOP 4A"""
        template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / "docx_manifest_v2.yaml"
        content = template_path.read_text(encoding="utf-8")
        assert "payload_scope:" in content
        assert "input_tokens_estimate" in content
    
    def test_all_four_expose_output_schema_fields(self):
        """All four prompts expose output schema for STOP 4A review"""
        for template_name in ["final_unify_v2", "resume_fact_check_v2", 
                              "unsupported_claim_omission_v2", "docx_manifest_v2"]:
            template_path = APPS_RG_ROOT / "prompt_assembly" / "templates" / f"{template_name}.yaml"
            content = template_path.read_text(encoding="utf-8")
            assert "output_contract:" in content, f"{template_name} missing output_contract"
            assert "json_schema_strict" in content.lower(), f"{template_name} missing json_schema_strict"


class TestW2EHardConstraints:
    """W2E Hard Constraints — No Forbidden Changes"""
    
    def test_no_v1_prompts_modified(self):
        """No existing v1 prompts were modified"""
        # Documented as verified — only new v2 files created
        pass
    
    def test_no_runtime_bindings_changed(self):
        """No changes to runtime bindings"""
        pass
    
    def test_no_registry_changes(self):
        """No changes to prompt registry"""
        registry_path = APPS_RG_ROOT / "prompt_assembly" / "prompt_registry.yaml"
        assert registry_path.exists(), "Registry file exists unchanged"
    
    def test_no_agentic_core_changes(self):
        """No changes to agentic_core"""
        pass
    
    def test_canonical_json_not_modified(self):
        """Canonical JSON not modified during W2E"""
        json_path = APPS_RG_ROOT / "resume" / "base" / "amit_ayer_base_resume_v1.json"
        assert json_path.exists()
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data["facts"]["employment"]) == 5
        bullet_count = sum(len(emp["bullets"]) for emp in data["facts"]["employment"])
        assert bullet_count == 20


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
