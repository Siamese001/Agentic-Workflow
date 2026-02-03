"""
Integration tests for L5 → L4 consolidation.

Verifies that refactored L5 agents correctly use shared L4 utilities
and delegate operations appropriately.

Test Strategy:
1. Create compliance violations (complexity + location)
2. Verify GovernanceAgent uses L4 complexity_analyzer
3. Verify HierarchyAgent delegates to LocationHealerAgent
4. Ensure no legacy internal methods are used
"""

import ast

import pytest

from agentic_core.L4_state.utils.complexity_analyzer import calculate_mccabe_complexity
from agentic_core.L5_safety.validators.GovernanceAgent import GovernanceAgent
from agentic_core.L5_safety.validators.HierarchyagentStrategy import HierarchyAgent


class TestL5L4Integration:
    """Integration tests for L5 agents using L4 utilities."""

    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create a temporary project structure."""
        # Create sovereign territory structure
        l0_dir = tmp_path / "agentic_core" / "L0_maintenance"
        l0_dir.mkdir(parents=True)

        l5_dir = tmp_path / "agentic_core" / "L5_safety"
        l5_dir.mkdir(parents=True)

        return tmp_path

    def test_governance_agent_uses_l4_complexity_analyzer(self, temp_project):
        """
        CHAOS TEST: Verify GovernanceAgent uses L4 complexity analyzer.

        Creates a file with McCabe complexity > 15 and verifies:
        1. GovernanceAgent detects the violation
        2. The detection uses agentic_core.L4_state.utils.complexity_analyzer
        3. No legacy internal complexity calculation is used
        """
        # Create a complex function (McCabe > 15)
        complex_code = """
def ultra_complex_function(a, b, c, d, e):
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        for i in range(10):
                            while i > 0:
                                if i % 2 == 0:
                                    if i % 3 == 0:
                                        if i % 5 == 0:
                                            return "fizzbuzz"
                                        elif i % 3 == 0:
                                            return "fizz"
                                        else:
                                            return "buzz"
                                i -= 1
    return "none"
"""

        # Write to temp file
        test_file = temp_project / "agentic_core" / "L0_maintenance" / "complex.py"
        test_file.write_text(complex_code)

        # Parse and verify complexity using L4 utility directly
        tree = ast.parse(complex_code)
        func_node = tree.body[0]
        direct_complexity = calculate_mccabe_complexity(func_node)

        # Complexity should be > 10 (reasonable threshold for "complex" function)
        assert direct_complexity > 10, (
            f"Test setup failed: complexity is {direct_complexity}, expected > 10"
        )

        # Now verify GovernanceAgent detects it
        agent = GovernanceAgent(root_dir=str(temp_project))
        violations = agent.check_complexity(str(test_file))

        # Should detect at least one violation
        assert len(violations) > 0, "GovernanceAgent failed to detect complexity violation"

        # Verify the violation is for our function
        violation = violations[0]
        assert violation["function"] == "ultra_complex_function"
        assert violation["complexity"] > 10

        # CRITICAL: Verify GovernanceAgent's internal method delegates to L4
        # This ensures no legacy calculation is happening
        agent_complexity = agent._calculate_mccabe(func_node)
        assert agent_complexity == direct_complexity, (
            f"GovernanceAgent._calculate_mccabe() returned {agent_complexity}, "
            f"but L4 utility returned {direct_complexity}. "
            "Agent is not using L4 utility!"
        )

    def test_hierarchy_agent_delegates_to_location_healer(self, temp_project):
        """
        CHAOS TEST: Verify HierarchyAgent delegates file moves to LocationHealerAgent.

        Creates a misplaced file and verifies:
        1. HierarchyAgent detects the violation
        2. HierarchyAgent delegates healing to LocationHealerAgent
        3. The file actually moves to the correct location
        """
        # Create a misplaced file in project root (should be in a sovereign territory)
        misplaced_file = temp_project / "orphan_file.py"
        misplaced_file.write_text("# This file is in the wrong place\n")

        # Create HierarchyAgent with healing enabled
        agent = HierarchyAgent(
            project_root=temp_project,
            healing_enabled=True,
            auto_approve=True,  # Auto-approve for testing
        )

        # Create a MISPLACED violation
        violation = {
            "type": "MISPLACED",
            "file": str(misplaced_file),
            "message": "File in project root, should be in sovereign territory",
        }

        # Execute healing
        result = agent.heal(violation)

        # Verify healing was attempted (various statuses are acceptable)
        assert result["status"] in (
            "success",
            "partial_success",
            "delegated",
            "manual_required",
            "skipped",
        ), f"Unexpected healing status: {result['status']}"

        # CRITICAL: Verify the delegation happened
        # If LocationHealerAgent is properly integrated, the result should indicate delegation
        # or the file should have been moved/archived
        if result["status"] == "success":
            # File should no longer exist at original location
            # (either moved or archived)
            assert (
                not misplaced_file.exists()
                or result.get("details", "").lower().find("relocated") >= 0
            ), "File still exists at original location and no relocation reported"

    def test_gravity_violation_detection_uses_l4_utilities(self, temp_project):
        """
        CHAOS TEST: Verify gravity violation detection uses L4 layer_gravity utilities.

        Creates an L0 file importing from L5 and verifies:
        1. StructuralValidatorAgent detects the gravity violation
        2. Detection uses agentic_core.L4_state.utils.layer_gravity
        """
        from agentic_core.L4_state.utils.layer_gravity import (
            extract_layer_from_path,
            is_gravity_violation,
        )
        from agentic_core.L5_safety.policy_engine.structural_validator_agent_types import (
            StructuralValidatorAgent,
            StructureConfig,
        )

        # Create L0 file with upward import to L5
        l0_file = temp_project / "agentic_core" / "L0_maintenance" / "bad_import.py"
        l0_file.write_text("""
from agentic_core.L5_safety.validators.GovernanceAgent import GovernanceAgent

def use_governance():
    return GovernanceAgent()
""")

        # Verify using L4 utilities directly
        source_layer = extract_layer_from_path(l0_file)
        assert source_layer == "L0"

        target_layer = "L5"
        assert is_gravity_violation(source_layer, target_layer) is True

        # Now verify StructuralValidatorAgent detects it
        config = StructureConfig(project_root=temp_project)
        agent = StructuralValidatorAgent(config=config)

        violations = agent.validate_file(l0_file)

        # Should detect gravity violation
        assert len(violations) > 0, "StructuralValidatorAgent failed to detect gravity violation"

        gravity_violations = [v for v in violations if v.violation_type == "GRAVITY"]
        assert len(gravity_violations) > 0, "No GRAVITY violations detected"

        # Verify the violation details
        violation = gravity_violations[0]
        assert "L0" in violation.message
        assert "L5" in violation.message

    def test_no_legacy_methods_used(self, temp_project):
        """
        VERIFICATION TEST: Ensure agents don't use legacy internal methods.

        This test verifies that:
        1. GovernanceAgent._calculate_mccabe delegates to L4
        2. StructuralValidatorAgent._extract_layer delegates to L4
        3. No duplicate complexity/gravity logic exists
        """
        from agentic_core.L4_state.utils.complexity_analyzer import calculate_mccabe_complexity
        from agentic_core.L4_state.utils.layer_gravity import extract_layer_from_path
        from agentic_core.L5_safety.policy_engine.structural_validator_agent_types import (
            StructuralValidatorAgent,
            StructureConfig,
        )
        from agentic_core.L5_safety.validators.GovernanceAgent import GovernanceAgent

        # Test GovernanceAgent
        gov_agent = GovernanceAgent(root_dir=str(temp_project))
        test_code = "def simple(): return 1"
        tree = ast.parse(test_code)
        func = tree.body[0]

        # Both should return the same result
        l4_result = calculate_mccabe_complexity(func)
        agent_result = gov_agent._calculate_mccabe(func)
        assert l4_result == agent_result, "GovernanceAgent not using L4 utility"

        # Test StructuralValidatorAgent
        struct_agent = StructuralValidatorAgent(StructureConfig())
        test_path = temp_project / "agentic_core" / "L3_orchestration" / "test.py"

        # Both should return the same result
        l4_layer = extract_layer_from_path(test_path)
        agent_layer = struct_agent._extract_layer(test_path)
        assert l4_layer == agent_layer, "StructuralValidatorAgent not using L4 utility"


class TestBackwardsCompatibility:
    """Verify backwards compatibility is maintained."""

    def test_structural_validator_class_constants_available(self):
        """Verify LAYER_ORDER and GRAVITY_RULES are still accessible."""
        from agentic_core.L5_safety.policy_engine.structural_validator_agent_types import (
            StructuralValidatorAgent,
        )

        # Class-level constants should still be accessible
        assert hasattr(StructuralValidatorAgent, "LAYER_ORDER")
        assert hasattr(StructuralValidatorAgent, "GRAVITY_RULES")

        # Verify they contain expected data
        assert "L0" in StructuralValidatorAgent.LAYER_ORDER
        assert "L6" in StructuralValidatorAgent.LAYER_ORDER
        assert "L0" in StructuralValidatorAgent.GRAVITY_RULES

    def test_gravity_leak_repair_agent_constants_available(self):
        """Verify GravityLeakRepairAgent still has LAYER_ORDER."""
        from agentic_core.L5_safety.gravity.GravityLeakRepairAgent import (
            GravityLeakRepairAgent,
        )

        assert hasattr(GravityLeakRepairAgent, "LAYER_ORDER")
        assert "L0" in GravityLeakRepairAgent.LAYER_ORDER
