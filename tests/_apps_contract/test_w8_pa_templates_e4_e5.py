"""W8: apps_rg PA Templates E4/E5 — All 8 Templates Resolution and Validation

Tests that verify:
- All 8 templates resolve from prompt_registry.yaml
- All 8 templates parse as valid YAML
- E4/E5 templates include required S0/D0/I0/C0/R0 slots
- resume_fact_check_v1 verifies against candidate_facts only
- unsupported_claim_omission_v1 contains omit-not-fabricate rules
- bullet_diversity_repair_v1 preserves citation/source IDs and factual fields
- docx_manifest_v1 is rendering-only
- W6 and W7 tests still pass (regression guard)
"""

import json

import pytest
import yaml

from apps_rg.prompt_assembly import PromptCompiler


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def compiler():
    """Fresh compiler instance for each test."""
    return PromptCompiler()


@pytest.fixture
def registry(compiler):
    """Loaded prompt registry."""
    return compiler.load_registry()


# =============================================================================
# All 8 Templates Resolution Tests
# =============================================================================

class TestAllTemplatesResolve:
    """All 8 templates must resolve from prompt_registry.yaml."""
    
    EXPECTED_TEMPLATES = [
        "strategic_tailor_v1",
        "tailor_existing_v1", 
        "generate_scratch_v1",
        "enhance_current_v1",
        "resume_fact_check_v1",
        "unsupported_claim_omission_v1",
        "bullet_diversity_repair_v1",
        "docx_manifest_v1",
    ]
    
    def test_all_eight_templates_in_registry(self, registry):
        """Registry must contain all 8 expected template entries."""
        templates = registry.get("templates", {})
        
        for template_id in self.EXPECTED_TEMPLATES:
            assert template_id in templates, f"Missing template: {template_id}"
    
    def test_strategic_tailor_v1_resolves(self, compiler):
        """strategic_tailor_v1 must resolve from registry."""
        template = compiler.resolve_template("strategic_tailor_v1")
        assert template["template_id"] == "strategic_tailor_v1"
        assert template["path"] == "templates/strategic_tailor_v1.yaml"
    
    def test_tailor_existing_v1_resolves(self, compiler):
        """tailor_existing_v1 must resolve from registry."""
        template = compiler.resolve_template("tailor_existing_v1")
        assert template["template_id"] == "tailor_existing_v1"
    
    def test_generate_scratch_v1_resolves(self, compiler):
        """generate_scratch_v1 must resolve from registry."""
        template = compiler.resolve_template("generate_scratch_v1")
        assert template["template_id"] == "generate_scratch_v1"
    
    def test_enhance_current_v1_resolves(self, compiler):
        """enhance_current_v1 must resolve from registry."""
        template = compiler.resolve_template("enhance_current_v1")
        assert template["template_id"] == "enhance_current_v1"
    
    def test_resume_fact_check_v1_resolves(self, compiler):
        """resume_fact_check_v1 must resolve from registry."""
        template = compiler.resolve_template("resume_fact_check_v1")
        assert template["template_id"] == "resume_fact_check_v1"
        assert template["allowed_stage"] == "E4_HEAL"
    
    def test_unsupported_claim_omission_v1_resolves(self, compiler):
        """unsupported_claim_omission_v1 must resolve from registry."""
        template = compiler.resolve_template("unsupported_claim_omission_v1")
        assert template["template_id"] == "unsupported_claim_omission_v1"
        assert template["allowed_stage"] == "E4_HEAL"
    
    def test_bullet_diversity_repair_v1_resolves(self, compiler):
        """bullet_diversity_repair_v1 must resolve from registry."""
        template = compiler.resolve_template("bullet_diversity_repair_v1")
        assert template["template_id"] == "bullet_diversity_repair_v1"
        assert template["allowed_stage"] == "E4_HEAL"
    
    def test_docx_manifest_v1_resolves(self, compiler):
        """docx_manifest_v1 must resolve from registry."""
        template = compiler.resolve_template("docx_manifest_v1")
        assert template["template_id"] == "docx_manifest_v1"
        assert template["allowed_stage"] == "E5_EXIT"


# =============================================================================
# Template Parsing Tests
# =============================================================================

class TestTemplateParsing:
    """All 8 templates must parse as valid YAML."""
    
    def test_strategic_tailor_v1_parses(self, compiler):
        """strategic_tailor_v1.yaml must be valid YAML."""
        template = compiler.load_template_file("templates/strategic_tailor_v1.yaml")
        assert template["template_id"] == "strategic_tailor_v1"
        assert "slot_bodies" in template
        assert "S0" in template["slot_bodies"]
    
    def test_tailor_existing_v1_parses(self, compiler):
        """tailor_existing_v1.yaml must be valid YAML."""
        template = compiler.load_template_file("templates/tailor_existing_v1.yaml")
        assert template["template_id"] == "tailor_existing_v1"
    
    def test_generate_scratch_v1_parses(self, compiler):
        """generate_scratch_v1.yaml must be valid YAML."""
        template = compiler.load_template_file("templates/generate_scratch_v1.yaml")
        assert template["template_id"] == "generate_scratch_v1"
    
    def test_enhance_current_v1_parses(self, compiler):
        """enhance_current_v1.yaml must be valid YAML."""
        template = compiler.load_template_file("templates/enhance_current_v1.yaml")
        assert template["template_id"] == "enhance_current_v1"
    
    def test_resume_fact_check_v1_parses(self, compiler):
        """resume_fact_check_v1.yaml must be valid YAML."""
        template = compiler.load_template_file("templates/resume_fact_check_v1.yaml")
        assert template["template_id"] == "resume_fact_check_v1"
        assert template["schema_version"] == "1.0"
    
    def test_unsupported_claim_omission_v1_parses(self, compiler):
        """unsupported_claim_omission_v1.yaml must be valid YAML."""
        template = compiler.load_template_file("templates/unsupported_claim_omission_v1.yaml")
        assert template["template_id"] == "unsupported_claim_omission_v1"
        assert template["schema_version"] == "1.0"
    
    def test_bullet_diversity_repair_v1_parses(self, compiler):
        """bullet_diversity_repair_v1.yaml must be valid YAML."""
        template = compiler.load_template_file("templates/bullet_diversity_repair_v1.yaml")
        assert template["template_id"] == "bullet_diversity_repair_v1"
        assert template["schema_version"] == "1.0"
    
    def test_docx_manifest_v1_parses(self, compiler):
        """docx_manifest_v1.yaml must be valid YAML."""
        template = compiler.load_template_file("templates/docx_manifest_v1.yaml")
        assert template["template_id"] == "docx_manifest_v1"
        assert template["schema_version"] == "1.0"


# =============================================================================
# E4/E5 Required Slots Tests
# =============================================================================

class TestE4E5RequiredSlots:
    """E4/E5 templates must include required S0/D0/I0/C0/R0 slots."""
    
    CORE_SLOTS = {"S0", "D0", "I0", "C0", "R0"}
    
    def test_resume_fact_check_v1_has_required_slots(self, registry):
        """resume_fact_check_v1 must have S0/D0/I0/C0/R0."""
        template = registry["templates"]["resume_fact_check_v1"]
        required = set(template["required_slots"])
        
        for slot in self.CORE_SLOTS:
            assert slot in required, f"Missing required slot: {slot}"
    
    def test_unsupported_claim_omission_v1_has_required_slots(self, registry):
        """unsupported_claim_omission_v1 must have S0/D0/I0/C0/R0."""
        template = registry["templates"]["unsupported_claim_omission_v1"]
        required = set(template["required_slots"])
        
        for slot in self.CORE_SLOTS:
            assert slot in required, f"Missing required slot: {slot}"
    
    def test_bullet_diversity_repair_v1_has_required_slots(self, registry):
        """bullet_diversity_repair_v1 must have S0/D0/I0/C0/R0."""
        template = registry["templates"]["bullet_diversity_repair_v1"]
        required = set(template["required_slots"])
        
        for slot in self.CORE_SLOTS:
            assert slot in required, f"Missing required slot: {slot}"
    
    def test_docx_manifest_v1_has_required_slots(self, registry):
        """docx_manifest_v1 must have S0/D0/I0/C0/R0."""
        template = registry["templates"]["docx_manifest_v1"]
        required = set(template["required_slots"])
        
        for slot in self.CORE_SLOTS:
            assert slot in required, f"Missing required slot: {slot}"


# =============================================================================
# Resume Fact-Check Template Content Tests
# =============================================================================

class TestResumeFactCheckContent:
    """resume_fact_check_v1 template content requirements."""
    
    def test_verifies_against_candidate_facts_only(self, compiler):
        """S0 must declare candidate_facts as sole ground truth."""
        template = compiler.load_template_file("templates/resume_fact_check_v1.yaml")
        s0_content = template["slot_bodies"]["S0"].lower()
        
        # Must declare candidate_facts as truth
        assert "candidate_facts" in s0_content
        assert "ground truth" in s0_content or "sole ground truth" in s0_content
        
        # Must distinguish JD as target context only
        assert "jd" in s0_content or "jd_requirements" in s0_content
        assert "not proof" in s0_content or "target context" in s0_content
    
    def test_no_fabrication_oath_present(self, compiler):
        """S0 must contain no-fabrication oath."""
        template = compiler.load_template_file("templates/resume_fact_check_v1.yaml")
        s0_content = template["slot_bodies"]["S0"].lower()
        
        assert "no-fabrication oath" in s0_content or "fabrication oath" in s0_content
    
    def test_metric_verification_required(self, compiler):
        """S0 must require metric verification."""
        template = compiler.load_template_file("templates/resume_fact_check_v1.yaml")
        s0_content = template["slot_bodies"]["S0"].lower()
        
        assert "metric" in s0_content
        assert "verify" in s0_content or "verification" in s0_content
    
    def test_output_schema_includes_findings(self, compiler):
        """R0 must define verification findings output."""
        template = compiler.load_template_file("templates/resume_fact_check_v1.yaml")
        r0_content = template["slot_bodies"]["R0"].lower()
        
        assert "verification" in r0_content or "findings" in r0_content
        assert "unsupported_claims" in r0_content or "sections" in r0_content


# =============================================================================
# Unsupported Claim Omission Template Content Tests
# =============================================================================

class TestUnsupportedClaimOmissionContent:
    """unsupported_claim_omission_v1 template content requirements."""
    
    def test_omit_not_fabricate_rules_present(self, compiler):
        """S0 must contain omit-not-fabricate rules."""
        template = compiler.load_template_file("templates/unsupported_claim_omission_v1.yaml")
        s0_content = template["slot_bodies"]["S0"].lower()
        
        # Must declare omit-only mode
        assert "omit" in s0_content
        assert "omit-only" in s0_content or "omit only" in s0_content
        
        # Must forbid adding new claims
        assert "must not add" in s0_content or "no filler" in s0_content
    
    def test_no_softening_rule_present(self, compiler):
        """S0 must forbid replacing strong claims with weaker unsupported claims."""
        template = compiler.load_template_file("templates/unsupported_claim_omission_v1.yaml")
        s0_content = template["slot_bodies"]["S0"].lower()
        
        assert "no softening" in s0_content or "softening" in s0_content
    
    def test_no_generalization_rule_present(self, compiler):
        """S0 must forbid generalizing specific claims."""
        template = compiler.load_template_file("templates/unsupported_claim_omission_v1.yaml")
        s0_content = template["slot_bodies"]["S0"].lower()
        
        assert "generalize" in s0_content or "filler" in s0_content
    
    def test_source_id_preservation_required(self, compiler):
        """S0 must require preserving source IDs."""
        template = compiler.load_template_file("templates/unsupported_claim_omission_v1.yaml")
        s0_content = template["slot_bodies"]["S0"].lower()
        
        assert "source" in s0_content and "preserve" in s0_content
    
    def test_omission_receipt_in_output(self, compiler):
        """R0 must include omitted_claims and gap_notes."""
        template = compiler.load_template_file("templates/unsupported_claim_omission_v1.yaml")
        r0_content = template["slot_bodies"]["R0"].lower()
        
        assert "omitted_claims" in r0_content
        assert "gap_notes" in r0_content or "gaps" in r0_content


# =============================================================================
# Bullet Diversity Repair Template Content Tests
# =============================================================================

class TestBulletDiversityRepairContent:
    """bullet_diversity_repair_v1 template content requirements."""
    
    def test_preserves_citation_source_ids(self, compiler):
        """S0 must require preserving citation/source IDs."""
        template = compiler.load_template_file("templates/bullet_diversity_repair_v1.yaml")
        s0_content = template["slot_bodies"]["S0"].lower()
        
        assert "source" in s0_content and "preserv" in s0_content
        assert "[source:" in s0_content or "citation" in s0_content
    
    def test_preserves_factual_fields(self, compiler):
        """S0 must require preserving metrics, dates, employers, titles, tools."""
        template = compiler.load_template_file("templates/bullet_diversity_repair_v1.yaml")
        s0_content = template["slot_bodies"]["S0"].lower()
        
        # Must list immutable facts
        assert "metrics" in s0_content and "immutable" in s0_content
        assert "dates" in s0_content
        assert "employer" in s0_content
        assert "titles" in s0_content or "job titles" in s0_content
        assert "tools" in s0_content
    
    def test_style_only_oath_present(self, compiler):
        """S0 must declare style-only mode."""
        template = compiler.load_template_file("templates/bullet_diversity_repair_v1.yaml")
        s0_content = template["slot_bodies"]["S0"].lower()
        
        assert "style-only" in s0_content or "style only" in s0_content
    
    def test_verb_replacement_rules_present(self, compiler):
        """S0 must include verb replacement rules."""
        template = compiler.load_template_file("templates/bullet_diversity_repair_v1.yaml")
        s0_content = template["slot_bodies"]["S0"].lower()
        
        assert "verb" in s0_content
        assert "replace" in s0_content or "replacement" in s0_content
    
    def test_no_metric_inflation_rule(self, compiler):
        """S0 must forbid metric inflation."""
        template = compiler.load_template_file("templates/bullet_diversity_repair_v1.yaml")
        s0_content = template["slot_bodies"]["S0"].lower()
        
        assert "metric inflation" in s0_content or "inflation" in s0_content
    
    def test_preservation_check_in_output(self, compiler):
        """R0 must include preservation_check."""
        template = compiler.load_template_file("templates/bullet_diversity_repair_v1.yaml")
        r0_content = template["slot_bodies"]["R0"].lower()
        
        assert "preservation_check" in r0_content or "preservation" in r0_content


# =============================================================================
# DOCX Manifest Template Content Tests
# =============================================================================

class TestDocxManifestContent:
    """docx_manifest_v1 template content requirements."""
    
    def test_rendering_only_oath_present(self, compiler):
        """S0 must declare rendering-only mode with no content changes."""
        template = compiler.load_template_file("templates/docx_manifest_v1.yaml")
        s0_content = template["slot_bodies"]["S0"].lower()
        
        assert "rendering-only" in s0_content or "rendering only" in s0_content
        assert "read-only" in s0_content or "read only" in s0_content
    
    def test_no_content_modification_rules(self, compiler):
        """S0 must explicitly forbid content modifications."""
        template = compiler.load_template_file("templates/docx_manifest_v1.yaml")
        s0_content = template["slot_bodies"]["S0"].lower()
        
        assert "must not" in s0_content or "prohibited" in s0_content
        assert "modify" in s0_content or "edit" in s0_content
    
    def test_preserves_evidence_authority(self, compiler):
        """S0 must require preserving evidence authority."""
        template = compiler.load_template_file("templates/docx_manifest_v1.yaml")
        s0_content = template["slot_bodies"]["S0"].lower()
        
        assert "source" in s0_content or "evidence" in s0_content
        assert "preserv" in s0_content or "maintain" in s0_content
    
    def test_layout_declaration_only(self, compiler):
        """I0 must focus on layout/ordering, not content."""
        template = compiler.load_template_file("templates/docx_manifest_v1.yaml")
        i0_content = template["slot_bodies"]["I0"].lower()
        
        assert "layout" in i0_content or "ordering" in i0_content or "section" in i0_content
        assert "font" in i0_content or "format" in i0_content or "render" in i0_content
    
    def test_content_preservation_in_output(self, compiler):
        """R0 must include content_preservation check."""
        template = compiler.load_template_file("templates/docx_manifest_v1.yaml")
        r0_content = template["slot_bodies"]["R0"].lower()
        
        assert "content_preservation" in r0_content or "preservation" in r0_content
        assert "modified_claim_count" in r0_content or "0" in r0_content


# =============================================================================
# Template Schema Version Tests
# =============================================================================

class TestTemplateSchemaVersions:
    """All templates must declare consistent schema versions."""
    
    def test_all_templates_schema_version_1_0(self, compiler):
        """All templates should declare schema_version 1.0."""
        templates = [
            "strategic_tailor_v1",
            "tailor_existing_v1",
            "generate_scratch_v1",
            "enhance_current_v1",
            "resume_fact_check_v1",
            "unsupported_claim_omission_v1",
            "bullet_diversity_repair_v1",
            "docx_manifest_v1",
        ]
        
        for template_id in templates:
            template = compiler.load_template_file(f"templates/{template_id}.yaml")
            assert template["schema_version"] == "1.0", f"{template_id} schema_version mismatch"


# =============================================================================
# Output Contract Tests
# =============================================================================

class TestOutputContracts:
    """All templates must declare valid output contracts."""
    
    def test_e4_templates_json_output(self, registry):
        """E4 templates must declare JSON output."""
        e4_templates = [
            "resume_fact_check_v1",
            "unsupported_claim_omission_v1",
            "bullet_diversity_repair_v1",
        ]
        
        for template_id in e4_templates:
            template = registry["templates"][template_id]
            contract = template["output_contract"]
            assert contract["format"] == "json", f"{template_id} format mismatch"
            assert contract["schema_ref"] == "rg_output_schema.json"
    
    def test_e5_template_json_output(self, registry):
        """E5 templates must declare JSON output."""
        template = registry["templates"]["docx_manifest_v1"]
        contract = template["output_contract"]
        assert contract["format"] == "json"


# =============================================================================
# Template File Existence Tests
# =============================================================================

class TestTemplateFileExistence:
    """All template files must exist on disk."""
    
    def test_resume_fact_check_v1_file_exists(self, compiler):
        """resume_fact_check_v1.yaml must exist."""
        path = compiler.base_path / "templates" / "resume_fact_check_v1.yaml"
        assert path.exists(), f"File not found: {path}"
    
    def test_unsupported_claim_omission_v1_file_exists(self, compiler):
        """unsupported_claim_omission_v1.yaml must exist."""
        path = compiler.base_path / "templates" / "unsupported_claim_omission_v1.yaml"
        assert path.exists(), f"File not found: {path}"
    
    def test_bullet_diversity_repair_v1_file_exists(self, compiler):
        """bullet_diversity_repair_v1.yaml must exist."""
        path = compiler.base_path / "templates" / "bullet_diversity_repair_v1.yaml"
        assert path.exists(), f"File not found: {path}"
    
    def test_docx_manifest_v1_file_exists(self, compiler):
        """docx_manifest_v1.yaml must exist."""
        path = compiler.base_path / "templates" / "docx_manifest_v1.yaml"
        assert path.exists(), f"File not found: {path}"
