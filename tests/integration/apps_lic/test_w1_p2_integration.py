"""W1 P2 Integration Completion Tests

Tests for P2 template slots and rubric dimensions added in W1.
"""

import pytest
from pathlib import Path
import yaml


class TestW1P2Templates:
    """Test P2 context slot integration in templates."""
    
    TEMPLATES_DIR = Path("apps_lic/prompt_assembly/templates")
    
    @pytest.mark.parametrize("template_file", [
        "outreach_draft_v1.yaml",
        "outreach_draft_v2.yaml",
        "compact_recruiter_arc.yaml",
        "exec_positioning.yaml",
    ])
    def test_template_has_p2_required_slots(self, template_file: str):
        """Verify all 4 templates have P2 context slots."""
        template_path = self.TEMPLATES_DIR / template_file
        assert template_path.exists(), f"Template {template_file} not found"
        
        content = template_path.read_text()
        
        # Check for P2 slot markers
        assert "N0  # P2: NarrativeArc" in content or "N0" in content, \
            f"{template_file} missing N0 slot"
        assert "A0  # P2: ArchetypeToneCalibration" in content or "A0" in content, \
            f"{template_file} missing A0 slot"
        assert "L0  # P2: CompetitiveLandscapeContext" in content or "L0" in content, \
            f"{template_file} missing L0 slot"
    
    @pytest.mark.parametrize("template_file", [
        "outreach_draft_v1.yaml",
        "outreach_draft_v2.yaml",
        "compact_recruiter_arc.yaml",
        "exec_positioning.yaml",
    ])
    def test_template_has_p2_slot_bodies(self, template_file: str):
        """Verify P2 slots have body definitions."""
        template_path = self.TEMPLATES_DIR / template_file
        content = template_path.read_text()
        
        # Check for slot body definitions
        assert "N0: |" in content, f"{template_file} missing N0 slot body"
        assert "A0: |" in content, f"{template_file} missing A0 slot body"
        assert "L0: |" in content, f"{template_file} missing L0 slot body"
    
    def test_outreach_draft_v2_has_p2_optional_inputs(self):
        """Verify v2 template marks P2 contexts as optional inputs."""
        template_path = self.TEMPLATES_DIR / "outreach_draft_v2.yaml"
        content = template_path.read_text()
        
        # Check optional inputs are listed
        assert "narrative_arc_context      # P2 optional" in content
        assert "archetype_tone_calibration  # P2 optional" in content
        assert "competitive_landscape_context  # P2 optional" in content
    
    def test_compact_recruiter_arc_has_recruiter_specific_guidance(self):
        """Verify recruiter template has P2 guidance for recruiter context."""
        template_path = self.TEMPLATES_DIR / "compact_recruiter_arc.yaml"
        content = template_path.read_text()
        
        # Check for recruiter-specific P2 guidance
        assert "For recruiters, use the compact arc only" in content
        assert "For recruiters, competitive differentiators are rarely relevant" in content
    
    def test_exec_positioning_has_exec_specific_guidance(self):
        """Verify exec template has P2 guidance for executive context."""
        template_path = self.TEMPLATES_DIR / "exec_positioning.yaml"
        content = template_path.read_text()
        
        # Check for executive-specific P2 guidance
        assert "For executives, arc coherence is critical" in content
        assert "arc_coherence_score must be >= 0.6" in content


class TestW1P2RubricDimensions:
    """Test P2 eval rubric dimensions."""
    
    RUBRICS_PATH = Path("apps_lic/config/domain_contract/eval_rubrics.yaml")
    THRESHOLDS_PATH = Path("apps_lic/config/domain_contract/threshold_profiles.yaml")
    
    def test_p2_dimensions_in_rubrics(self):
        """Verify 3 P2 dimensions added to eval rubrics."""
        content = self.RUBRICS_PATH.read_text()
        
        # Check for P2 dimension IDs
        assert "dimension_id: narrative_coherence" in content
        assert "dimension_id: tone_register_fit" in content
        assert "dimension_id: differentiator_grounded" in content
    
    def test_p2_dimension_weights(self):
        """Verify P2 dimensions have appropriate weights."""
        rubrics = yaml.safe_load(self.RUBRICS_PATH.read_text())
        
        # Find apps_lic outreach rubric
        lic_rubric = None
        for rubric in rubrics:
            if rubric.get("app_id") == "apps_lic":
                lic_rubric = rubric
                break
        
        assert lic_rubric is not None, "apps_lic rubric not found"
        
        # Check P2 dimension weights
        dim_weights = {d["dimension_id"]: d["weight"] for d in lic_rubric["score_dimensions"]}
        
        assert "narrative_coherence" in dim_weights
        assert dim_weights["narrative_coherence"] == 0.08
        
        assert "tone_register_fit" in dim_weights
        assert dim_weights["tone_register_fit"] == 0.08
        
        assert "differentiator_grounded" in dim_weights
        assert dim_weights["differentiator_grounded"] == 0.05
    
    def test_p2_grader_types(self):
        """Verify P2 dimensions have correct grader types."""
        rubrics = yaml.safe_load(self.RUBRICS_PATH.read_text())
        
        lic_rubric = None
        for rubric in rubrics:
            if rubric.get("app_id") == "apps_lic":
                lic_rubric = rubric
                break
        
        dim_graders = {d["dimension_id"]: d["grader_type"] 
                      for d in lic_rubric["score_dimensions"]}
        
        # narrative_coherence and tone_register_fit are LLM judges
        assert dim_graders["narrative_coherence"] == "llm_as_judge"
        assert dim_graders["tone_register_fit"] == "llm_as_judge"
        
        # differentiator_grounded is state_check (deterministic)
        assert dim_graders["differentiator_grounded"] == "state_check"
    
    def test_p2_thresholds_in_profiles(self):
        """Verify P2 dimensions have threshold minimums."""
        content = self.THRESHOLDS_PATH.read_text()
        
        # Check for P2 dimension thresholds
        assert "narrative_coherence: 0.70" in content
        assert "tone_register_fit: 0.75" in content
        assert "differentiator_grounded: 1.0" in content
    
    def test_p2_dimension_descriptions(self):
        """Verify P2 dimensions have descriptive text."""
        content = self.RUBRICS_PATH.read_text()
        
        # Check for descriptive text
        assert "P2a: Arc sections flow logically" in content
        assert "P2b: Vocabulary and formality level match the archetype" in content
        assert "P2c: Any competitive differentiator claim is backed by source_refs" in content


class TestW1P2JudgePrompts:
    """Test P2 judge prompts in prompts.json."""
    
    PROMPTS_PATH = Path("apps_lic/config/prompts.json")
    
    def test_narrative_coherence_judge_prompt_exists(self):
        """Verify narrative coherence judge prompt exists."""
        import json
        prompts = json.loads(self.PROMPTS_PATH.read_text())
        
        assert "judge_narrative_coherence" in prompts
        template = prompts["judge_narrative_coherence"]["template"]
        
        assert "Evaluate this outreach message for narrative coherence" in template
        assert "{message_body}" in template
        assert "{recommended_order}" in template
        assert "score" in template.lower()
    
    def test_tone_register_fit_judge_prompt_exists(self):
        """Verify tone register fit judge prompt exists."""
        import json
        prompts = json.loads(self.PROMPTS_PATH.read_text())
        
        assert "judge_tone_register_fit" in prompts
        template = prompts["judge_tone_register_fit"]["template"]
        
        assert "Evaluate this outreach message for tone-register fit" in template
        assert "{message_body}" in template
        assert "{archetype_id}" in template
        assert "score" in template.lower()
    
    def test_judge_prompts_return_json(self):
        """Verify judge prompts request JSON output."""
        import json
        prompts = json.loads(self.PROMPTS_PATH.read_text())
        
        for prompt_key in ["judge_narrative_coherence", "judge_tone_register_fit"]:
            template = prompts[prompt_key]["template"]
            assert "JSON" in template, f"{prompt_key} should request JSON output"


class TestW1SpineWiring:
    """Test spine wiring verification for P2 components."""
    
    def test_spine_wiring_has_p2_verifiers(self):
        """Verify spine wiring includes P2 template and rubric verifiers."""
        wiring_path = Path("apps_lic/spine_wiring.py")
        content = wiring_path.read_text()
        
        # Check for P2 component names in COMPONENTS list
        assert '"p2_templates"' in content or "'p2_templates'" in content
        assert '"p2_rubric_dims"' in content or "'p2_rubric_dims'" in content
        
        # Check for verification methods
        assert "_verify_p2_templates" in content
        assert "_verify_p2_rubric_dims" in content
    
    def test_p2_template_verifier_checks_all_templates(self):
        """Verify P2 template verifier checks all 4 templates."""
        wiring_path = Path("apps_lic/spine_wiring.py")
        content = wiring_path.read_text()
        
        # Check for all 4 template names
        assert "outreach_draft_v1.yaml" in content
        assert "outreach_draft_v2.yaml" in content
        assert "compact_recruiter_arc.yaml" in content
        assert "exec_positioning.yaml" in content


class TestW1GracefulDegradation:
    """Test graceful degradation when P2 contexts absent."""
    
    TEMPLATES_DIR = Path("apps_lic/prompt_assembly/templates")
    
    @pytest.mark.parametrize("template_file", [
        "outreach_draft_v1.yaml",
        "outreach_draft_v2.yaml",
        "compact_recruiter_arc.yaml",
        "exec_positioning.yaml",
    ])
    def test_p2_slots_have_graceful_fallback(self, template_file: str):
        """Verify all P2 slots have graceful fallback language."""
        template_path = self.TEMPLATES_DIR / template_file
        content = template_path.read_text()
        
        # Check for graceful fallback patterns in P2 slots
        # Each P2 slot should have "If no ... proceed without" or similar
        assert "If no narrative arc context" in content or "proceed without this guidance" in content
        assert "If no calibration" in content or "use default" in content
        assert "If no competitive context" in content or "omit competitive framing" in content
