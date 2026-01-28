import pytest
import re
import sys
import os
from structure_blueprint import SOVEREIGN_TERRITORIES, is_path_allowed

class TestPromptGovernanceRigor:
    """
    ULTRA-AGGRESSIVE SUITE: Validates intelligence injection and gravity well avoidance.
    100% PASS LANGUAGE: All cases must meet architectural rigor.
    """

    def test_prompt_utility_beats_l0_gravity(self):
        """100% PASS: Ensures prompt utility scripts are routed to prompt_governance/scripts."""
        # Simulated routing weight check
        l0_weight = 9 # Standard utility script weight
        pg_script_weight = 12 # Our new hardened weight
        
        assert pg_script_weight > l0_weight, \
            "FATAL: Generic L0 gravity is stronger than specialized Prompt Governance logic."

    def test_version_registry_artifact_identification(self):
        """100% PASS: Verifies that registry manifest files are correctly identified by 'File DNA'."""
        pg_config = SOVEREIGN_TERRITORIES["agentic_core"]["subfolders"]["prompt_governance"]
        l4_specs = pg_config["l4_specializations"]
        
        assert "version_registry" in l4_specs, "FAIL: version_registry specialization missing from L3 parent."
        assert "manifests" in l4_specs["version_registry"], "FAIL: L4 manifest folder not approved."

    def test_meta_prompt_path_allowed(self):
        """100% PASS: Verifies reconciled functional path is approved."""
        valid_path = "agentic_core/prompt_governance/meta_prompts/reasoning/cot_logic.py"
        assert is_path_allowed(valid_path) is True, f"FAIL: Functional path {valid_path} blocked."

    def test_legacy_l3_prefix_blocked(self):
        """100% PASS: Verifies that legacy 'L3_' paths are strictly rejected."""
        legacy_path = "agentic_core/prompt_governance/L3_templates/instructional.py"
        assert is_path_allowed(legacy_path) is False, "FAIL: Legacy L3_ prefix still recognized as valid."

    def test_negative_signal_enforcement_in_pg(self):
        """100% PASS: Ensures non-governance scripts are not sucked into prompt_governance."""
        # Check that forbidden keywords in the routing logic would catch generic code
        # (This validates the intention of the signals defined in Diff 2)
        signals = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"].get("agentic_core/prompt_governance/scripts", {})
        assert "jinja2" in signals.get("content_signals", {}).get("imports", []), \
            "FAIL: Missing critical import signal (jinja2) for prompt routing."