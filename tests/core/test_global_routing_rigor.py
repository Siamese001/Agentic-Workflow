"""
ULTRA-AGGRESSIVE GLOBAL ROUTING RIGOR TEST SUITE
Validates 100% pass across all core gravity wells and weight hierarchy enforcement.

This suite ensures the Global Weight Standard is properly enforced:
- 100 (Constitutional): base_agents
- 20-25 (Critical Safety): L5_safety (Guardrails, Gravity)
- 15-18 (Domain Logic): prompt_governance, L1_cognition, L3_orchestration
- 10-14 (State & Schema): L4_state, schemas/models, version_registry
- 5-9 (Generic Utilities): L0_maintenance, L2_execution (Tool Registry)
"""
import pytest
from agentic_core.L5_safety.validators.structure_blueprint import SOVEREIGN_TERRITORIES


class TestGlobalRoutingRigor:
    """
    ULTRA-AGGRESSIVE SUITE: Validates 100% pass across all core gravity wells.
    """

    def test_safety_beats_cognition(self):
        """100% PASS: L5 Safety (25) must outrank L1 Cognition (18)."""
        safety_w = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]["agentic_core/L5_safety/guardrails"]["weight"]
        cognition_w = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]["agentic_core/L1_cognition/thought_engine"]["weight"]
        assert safety_w > cognition_w, "FATAL: Cognitive reasoning can bypass safety guardrails!"
        assert safety_w == 25, f"FAIL: Safety guardrails expected weight 25, got {safety_w}"
        assert cognition_w == 18, f"FAIL: Cognition expected weight 18, got {cognition_w}"

    def test_orchestration_beats_execution(self):
        """100% PASS: L3 Orchestration (16) must outrank L2 Execution (9)."""
        orch_w = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]["agentic_core/L3_orchestration/workflow_engines"]["weight"]
        exec_w = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]["agentic_core/L2_execution/tool_registry"]["weight"]
        assert orch_w > exec_w, "FATAL: Simple tool logic is shadowing workflow orchestration!"
        assert orch_w == 16, f"FAIL: Orchestration expected weight 16, got {orch_w}"
        assert exec_w == 9, f"FAIL: Execution expected weight 9, got {exec_w}"

    def test_state_beats_generic_scripts(self):
        """100% PASS: L4 State (14) must outrank L0 Generic Utilities (9)."""
        state_w = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]["agentic_core/L4_state/validation_context"]["weight"]
        # Generic baseline is 9 (defined in L2/L0 utility patterns)
        assert state_w > 9, "FATAL: Persistence contexts are losing gravity to maintenance scripts!"
        assert state_w == 14, f"FAIL: State validation expected weight 14, got {state_w}"

    def test_gravity_enforcement_priority(self):
        """100% PASS: Gravity logic (22) must be second only to Base Agents (100)."""
        gravity_w = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]["agentic_core/L5_safety/gravity"]["weight"]
        base_w = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]["agentic_core/base_agents"]["weight"]
        
        assert gravity_w > 20, "FAIL: Gravity signals are too weak to enforce layer boundaries."
        assert gravity_w == 22, f"FAIL: Gravity expected weight 22, got {gravity_w}"
        assert base_w == 100, "FAIL: Base Agents have lost Constitutional Priority."

    def test_prompt_governance_domain_priority(self):
        """100% PASS: Prompt governance (15) must beat generic utilities but not exceed domain logic."""
        pg_w = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]["agentic_core/prompt_governance/meta_prompts"]["weight"]
        
        assert pg_w == 15, f"FAIL: Prompt governance expected weight 15, got {pg_w}"
        assert pg_w > 9, "FAIL: Prompt governance losing to generic utilities!"
        assert pg_w < 18, "FAIL: Prompt governance exceeding cognitive reasoning priority!"

    def test_version_registry_schema_priority(self):
        """100% PASS: Version registry (10) must be in schema/state tier."""
        vr_w = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]["agentic_core/prompt_governance/version_registry"]["weight"]
        
        assert vr_w == 10, f"FAIL: Version registry expected weight 10, got {vr_w}"
        assert vr_w > 9, "FAIL: Version registry losing to generic utilities!"
        assert vr_w < 14, "FAIL: Version registry exceeding state management priority!"

    def test_no_weight_collisions(self):
        """100% PASS: Ensures no two specialized domains have identical weights."""
        signals = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]
        weights = [s["weight"] for s in signals.values()]
        # Filter for weights between 10 and 30 (the "conflict zone")
        conflict_zone = [w for w in weights if 10 <= w <= 30]
        assert len(conflict_zone) == len(set(conflict_zone)), \
            f"COLLISION: Found identical weights in the conflict zone: {conflict_zone}"

    def test_global_weight_hierarchy_compliance(self):
        """100% PASS: Validates complete Global Weight Standard compliance."""
        expected_hierarchy = {
            100: ["agentic_core/base_agents"],
            25: ["agentic_core/L5_safety/guardrails"],
            22: ["agentic_core/L5_safety/gravity"],
            18: ["agentic_core/L1_cognition/thought_engine"],
            16: ["agentic_core/L3_orchestration/workflow_engines"],
            15: ["agentic_core/prompt_governance/meta_prompts"],
            14: ["agentic_core/L4_state/validation_context"],
            12: ["agentic_core/prompt_governance/scripts"],
            10: ["agentic_core/prompt_governance/version_registry"],
            9: ["agentic_core/L2_execution/tool_registry"]
        }
        
        signals = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]
        
        for expected_weight, expected_paths in expected_hierarchy.items():
            for path in expected_paths:
                assert path in signals, f"FAIL: Missing expected path {path}"
                actual_weight = signals[path]["weight"]
                assert actual_weight == expected_weight, \
                    f"FAIL: {path} expected weight {expected_weight}, got {actual_weight}"

    def test_critical_safety_weight_range(self):
        """100% PASS: L5 Safety components must be in 20-25 range."""
        guardrails_w = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]["agentic_core/L5_safety/guardrails"]["weight"]
        gravity_w = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]["agentic_core/L5_safety/gravity"]["weight"]
        
        assert 20 <= guardrails_w <= 25, f"FAIL: Guardrails weight {guardrails_w} not in critical safety range 20-25"
        assert 20 <= gravity_w <= 25, f"FAIL: Gravity weight {gravity_w} not in critical safety range 20-25"

    def test_domain_logic_weight_range(self):
        """100% PASS: Domain logic components must be in 15-18 range."""
        cognition_w = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]["agentic_core/L1_cognition/thought_engine"]["weight"]
        orchestration_w = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]["agentic_core/L3_orchestration/workflow_engines"]["weight"]
        pg_w = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]["agentic_core/prompt_governance/meta_prompts"]["weight"]
        
        assert 15 <= cognition_w <= 18, f"FAIL: Cognition weight {cognition_w} not in domain logic range 15-18"
        assert 15 <= orchestration_w <= 18, f"FAIL: Orchestration weight {orchestration_w} not in domain logic range 15-18"
        assert 15 <= pg_w <= 18, f"FAIL: Prompt governance weight {pg_w} not in domain logic range 15-18"

    def test_state_schema_weight_range(self):
        """100% PASS: State & schema components must be in 10-14 range."""
        state_w = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]["agentic_core/L4_state/validation_context"]["weight"]
        version_w = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]["agentic_core/prompt_governance/version_registry"]["weight"]
        
        assert 10 <= state_w <= 14, f"FAIL: State weight {state_w} not in state & schema range 10-14"
        assert 10 <= version_w <= 14, f"FAIL: Version registry weight {version_w} not in state & schema range 10-14"

    def test_generic_utilities_weight_range(self):
        """100% PASS: Generic utilities must be in 5-9 range."""
        execution_w = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]["agentic_core/L2_execution/tool_registry"]["weight"]
        
        assert 5 <= execution_w <= 9, f"FAIL: Execution weight {execution_w} not in generic utilities range 5-9"

    def test_base_agents_constitutional_priority(self):
        """100% PASS: Base agents must maintain constitutional weight 100."""
        base_w = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]["agentic_core/base_agents"]["weight"]
        
        assert base_w == 100, f"FAIL: Base agents lost constitutional priority with weight {base_w}"
        
        # Ensure no other component comes close to constitutional priority
        signals = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]
        other_weights = [s["weight"] for path, s in signals.items() if path != "agentic_core/base_agents"]
        max_other_weight = max(other_weights)
        assert max_other_weight <= 25, f"FAIL: Non-base component has weight {max_other_weight}, too close to constitutional 100"


if __name__ == "__main__":
    # Run the test suite directly
    pytest.main([__file__, "-v"])
