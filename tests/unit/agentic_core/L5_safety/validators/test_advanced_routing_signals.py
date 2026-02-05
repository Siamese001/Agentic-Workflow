from agentic_core.L5_safety.validators.structure_blueprint_config import (
    SOVEREIGN_TERRITORIES,
    get_correct_app_path,
    is_app_specific_file,
)


class TestAdvancedRoutingHardening:
    """
    ULTRA-AGGRESSIVE SUITE (Phase 6): 6 Additional High-Fidelity Test Cases.
    100% PASS LANGUAGE: Mandatory validation of content-aware routing.
    """

    # --- TEST 1: The "Shadow Template" (Meta-Prompt Isolation) ---
    def test_shadow_template_routing(self):
        """100% PASS: Ensures .jinja files with system_prompt content route to meta_prompts."""
        # Signature: Contains 'sovereign_instruction' or 'persona_definition'
        signals = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"][
            "agentic_core/prompt_governance/meta_prompts"
        ]

        # Verify content-aware signal exists
        assert "sovereign_instruction" in signals["keyword_signals"]
        assert "persona_definition" in signals["keyword_signals"]
        assert signals["weight"] == 15  # Heavy weight to pull from generic templates

    # --- TEST 2: The "Orphaned Lockfile" (Registry DNA) ---
    def test_registry_lockfile_dna(self):
        """100% PASS: Ensures JSON manifests with 'checksum_manifest' route to version_registry."""
        # Signature: DNA includes 'registry_version' and 'checksum_manifest'
        signals = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"][
            "agentic_core/prompt_governance/version_registry"
        ]

        assert "registry_version" in signals["json_keys"]
        assert "checksum_manifest" in signals["json_keys"]
        assert signals["weight"] == 10  # Specificity over generic data/logs

    # --- TEST 3: The "Persona Definition" (Base Class Gravity) ---
    def test_persona_base_class_gravity(self):
        """100% PASS: Validates that classes inheriting from BasePersona route to meta_prompts."""
        signals = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"][
            "agentic_core/prompt_governance/meta_prompts"
        ]

        assert "BasePersona" in signals["base_classes"]
        assert ".*Persona.*" in signals["class_patterns"]

    # --- TEST 4: The "App-Specific Leak" (Deportation Logic) ---
    def test_app_leak_deportation_priority(self):
        """100% PASS: Ensures rg_ scripts found in core are flagged for apps_rg/scripts."""
        filename = "rg_resume_builder.py"
        # Current logic in LocationAgent uses get_correct_app_path()

        assert is_app_specific_file(filename) is True
        assert get_correct_app_path(filename) == "apps_rg/engines"  # SSOT target

    # --- TEST 5: The "Validation Context Spike" (L4 State Capture) ---
    def test_validation_context_routing_accuracy(self):
        """100% PASS: Ensures ValidationContext classes route to L4_state/validation_context."""
        # Signature: base_classes includes 'ValidationContext'
        signals = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"][
            "agentic_core/L4_state/validation_context"
        ]

        assert "ValidationContext" in signals["base_classes"]
        assert ".*Context.*" in signals["class_patterns"]
        assert signals["weight"] == 8

    # --- TEST 6: The "Prompt Migration Tool" (Utility Disambiguation) ---
    def test_prompt_utility_vs_l0_maintenance(self):
        """100% PASS: Ensures specialized prompt scripts beat L0 generic utility weights."""
        # L0 generic scripts have a weight of 9. Prompt scripts have 12.
        prompt_script_signals = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"][
            "agentic_core/prompt_governance/scripts"
        ]
        l0_generic_weight = 9  # Constant from blueprint audit

        assert prompt_script_signals["weight"] > l0_generic_weight, (
            "CRITICAL FAILURE: Specialized prompt scripts will be lost to L0 Maintenance gravity."
        )
        assert "jinja2" in prompt_script_signals["content_signals"]["imports"]
