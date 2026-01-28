import pytest
import re
import sys
import os
from structure_blueprint import is_path_allowed, SOVEREIGN_TERRITORIES, get_correct_app_path

class TestGlobalIntelligenceRigor:
    """
    ULTRA-AGGRESSIVE SUITE (Phase 7): 10 Detailed Multi-Domain Test Cases.
    Ensures specialized domains always 'win' the gravity conflict.
    """

    # --- CASE 1: Safety Dominance ---
    def test_safety_outranks_cognition(self):
        """100% PASS: L5 Safety (25) must shadow L1 Cognition (18) for overlapping terms."""
        safety_w = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]["agentic_core/L5_safety/guardrails"]["weight"]
        cognition_w = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]["agentic_core/L1_cognition/thought_engine"]["weight"]
        assert safety_w > cognition_w, "FATAL: Cognitive reasoning signals are too heavy relative to safety."

    # --- CASE 2: Strategic Orchestration vs Execution ---
    def test_orchestration_outranks_execution(self):
        """100% PASS: L3 Orchestration (16) must shadow L2 Execution (9)."""
        orch_w = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]["agentic_core/L3_orchestration/workflow_engines"]["weight"]
        exec_w = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]["agentic_core/L2_execution/tool_registry"]["weight"]
        assert orch_w > exec_w, "FATAL: Low-level tool logic is shadowing strategic workflow engines."

    # --- CASE 3: Prompt Script Gravity Isolation ---
    def test_prompt_utility_wins_over_generic_l0(self):
        """100% PASS: Specialized Prompt Scripts (12) must beat Generic L0 Maintenance (9)."""
        pg_script_w = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]["agentic_core/prompt_governance/scripts"]["weight"]
        # Generic maintenance baseline is 9
        assert pg_script_w > 9, "CRITICAL: Specialized prompt utilities will be misrouted to L0 maintenance."

    # --- CASE 4: State Integrity vs Versioning ---
    def test_state_integrity_priority(self):
        """100% PASS: L4 Validation Context (14) must outrank Versioning (11)."""
        state_w = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]["agentic_core/L4_state/validation_context"]["weight"]
        version_w = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]["agentic_core/prompt_governance/version_registry"]["weight"]
        assert state_w > version_w, "FAIL: State integrity contexts are losing priority to registry manifests."

    # --- CASE 5: Legacy Prefix Rejection (L3_) ---
    def test_legacy_l3_prefix_blocked_in_reconciled_pg(self):
        """100% PASS: Verifies nested forbidden patterns block legacy 'L3_' folders."""
        legacy_path = "agentic_core/prompt_governance/L3_templates/meta_prompts.py"
        assert is_path_allowed(legacy_path) is False, "FAIL: Legacy L3_ structure still permitted."

    # --- CASE 6: File DNA: Registry Manifest ---
    def test_registry_manifest_dna_identification(self):
        """100% PASS: Ensures 'checksum_manifest' key correctly identifies version_registry files."""
        signals = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]["agentic_core/prompt_governance/version_registry"]
        assert "checksum_manifest" in signals["json_keys"], "FAIL: DNA signal missing for registry artifacts."

    # --- CASE 7: App-Specific Deportation ---
    def test_rg_prefix_deportation(self):
        """100% PASS: Ensures 'rg_' prefixed files are strictly routed to apps_rg/engines."""
        assert get_correct_app_path("rg_builder.py") == "apps_rg/engines"

    # --- CASE 8: Base Agent Constitutional Priority ---
    def test_base_agent_absolute_priority(self):
        """100% PASS: Base Agents must always be weight 100."""
        base_w = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]["agentic_core/base_agents"]["weight"]
        assert base_w == 100, "FAIL: Foundation agents lost constitutional priority."

    # --- CASE 9: Global Weight Collision Check ---
    def test_no_weight_collisions_in_conflict_zone(self):
        """100% PASS: Every core domain must have a unique weight to prevent arbitrary ties."""
        signals = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]
        weights = [s["weight"] for s in signals.values()]
        # Filter for the conflict zone (10-30)
        conflict_zone = [w for w in weights if 10 <= w <= 30]
        assert len(conflict_zone) == len(set(conflict_zone)), f"COLLISION: Found identical weights: {conflict_zone}"

    # --- CASE 10: Persona Signal Accuracy ---
    def test_persona_signals_for_meta_prompts(self):
        """100% PASS: Ensures 'persona_definition' pulls files into meta_prompts (15)."""
        signals = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]["agentic_core/prompt_governance/meta_prompts"]
        assert "persona_definition" in signals["keyword_signals"]
        assert signals["weight"] == 15