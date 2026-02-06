#!/usr/bin/env python3
"""
Guardian Integration Tests
Tests cross-component interactions and end-to-end scenarios.
"""

import sys
import time
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.guardian.base import AgentTestMixin, GuardianTestBase


class TestGuardianIntegration(AgentTestMixin):
    """Integration tests for Guardian suite components."""

    def test_base_classes_functional(self):
        """Test that base classes work correctly."""
        root = GuardianTestBase.get_project_root()
        assert root.exists()
        assert (root / "agentic_core").exists()

    def test_agent_scanning_functional(self):
        """Test that agent scanning works across all territories."""
        agents = GuardianTestBase.scan_agents()
        assert len(agents) > 0, "Should find at least one agent"

        agent_paths = [str(a) for a in agents]
        has_agentic_core = any("agentic_core" in p for p in agent_paths)
        assert has_agentic_core, "Should find agents in agentic_core"

    def test_ast_parsing_functional(self):
        """Test that AST parsing works on real agent files."""
        agents = GuardianTestBase.scan_agents()

        parsed_count = 0
        for agent_file in agents[:10]:
            tree = GuardianTestBase.parse_ast(agent_file)
            if tree:
                parsed_count += 1

        assert parsed_count > 0, "Should successfully parse at least one agent"

    def test_layer_hierarchy_detection(self):
        """Test that layer hierarchy detection works correctly."""
        test_paths = [
            (Path("agentic_core/L0_maintenance/test.py"), "L0_maintenance", 0),
            (Path("agentic_core/L5_safety/test.py"), "L5_safety", 5),
            (Path("apps_lic/test.py"), None, -1),
        ]

        for path, expected_layer, expected_level in test_paths:
            result = GuardianTestBase.check_layer_hierarchy(path)
            assert result["layer"] == expected_layer, f"Expected layer {expected_layer} for {path}"
            assert result["level"] == expected_level, f"Expected level {expected_level} for {path}"

    def test_agent_class_detection(self):
        """Test that agent class detection works correctly."""
        code = """
class TestAgent:
    def run(self):
        pass

class AnotherAgent:
    pass

class NotAnAgent:
    pass
"""
        temp_file = self.create_temp_file(code)
        try:
            tree = GuardianTestBase.parse_ast(temp_file)
            assert tree is not None

            agent_classes = GuardianTestBase.find_agent_classes(tree)
            assert len(agent_classes) == 2

            class_names = [cls.name for cls in agent_classes]
            assert "TestAgent" in class_names
            assert "AnotherAgent" in class_names
            assert "NotAnAgent" not in class_names
        finally:
            self.cleanup_temp_file(temp_file)

    def test_method_extraction(self):
        """Test that method extraction works correctly."""
        code = """
class TestAgent:
    def __init__(self):
        pass

    def run(self):
        pass

    def heal_repository(self):
        pass

    async def async_method(self):
        pass
"""
        temp_file = self.create_temp_file(code)
        try:
            tree = GuardianTestBase.parse_ast(temp_file)
            agent_classes = GuardianTestBase.find_agent_classes(tree)

            methods = GuardianTestBase.get_class_methods(agent_classes[0])
            assert "__init__" in methods
            assert "run" in methods
            assert "heal_repository" in methods
            assert "async_method" in methods
        finally:
            self.cleanup_temp_file(temp_file)

    def test_cross_layer_validation(self, layer_hierarchy):
        """Test validation across architectural layers."""
        assert layer_hierarchy["L5_safety"] > layer_hierarchy["L1_cognition"]
        assert layer_hierarchy["L0_maintenance"] < layer_hierarchy["L6_observability"]

    def test_performance_benchmarks(self, guardian_performance_baseline):
        """Ensure Guardian tests meet performance targets."""
        start_time = time.time()

        agent_files = GuardianTestBase.scan_agents()

        scan_time = time.time() - start_time

        max_time = guardian_performance_baseline["max_test_time_seconds"]
        assert scan_time < max_time, f"Agent scan took {scan_time:.2f}s, expected < {max_time}s"

        max_agents = guardian_performance_baseline["max_agents_to_scan"]
        assert len(agent_files) <= max_agents, f"Found {len(agent_files)} agents, expected <= {max_agents}"

    def test_session_fixtures_available(self, agent_registry, layer_hierarchy, territories):
        """Test that session fixtures are available and functional."""
        assert isinstance(agent_registry, dict)
        assert isinstance(layer_hierarchy, dict)
        assert isinstance(territories, list)

        assert len(layer_hierarchy) == 7
        assert "agentic_core" in territories


class TestValidatorIntegration(AgentTestMixin):
    """Integration tests for validator components."""

    def test_agent_autonomy_validator_integration(self):
        """Test agent autonomy validator works with real code."""
        from tests.guardian.test_agent_autonomy import AgentAutonomyValidator

        compliant_code = """
class TestAgent:
    def heal_repository(self):
        pass
"""
        temp_file = self.create_temp_file(compliant_code)
        try:
            result = AgentAutonomyValidator.validate_agent_file(temp_file)
            assert result["compliant"]
        finally:
            self.cleanup_temp_file(temp_file)

    def test_agent_validation_validator_integration(self):
        """Test agent validation validator works with real code."""
        from tests.guardian.test_agent_validation import AgentStructureValidator

        valid_code = """
class TestAgent:
    def __init__(self):
        pass

    def run(self):
        pass
"""
        temp_file = self.create_temp_file(valid_code, suffix="Agent.py")
        try:
            result = AgentStructureValidator.check_agent_structure(temp_file)
            assert result["has_agent_class"]
            assert result["has_init"]
            assert result["has_run_method"]
        finally:
            self.cleanup_temp_file(temp_file)

    def test_architecture_governance_validator_integration(self, tmp_path):
        """Test architecture governance validator works with real code."""
        from tests.guardian.test_architecture_governance import ArchitectureGovernanceValidator

        valid_code = """
class TestAgent:
    def run(self):
        pass
"""
        layer_dir = tmp_path / "temp_agentic_core" / "L5_safety"
        layer_dir.mkdir(parents=True)
        temp_file = layer_dir / "TestAgent.py"
        temp_file.write_text(valid_code)

        result = ArchitectureGovernanceValidator.validate_file(temp_file)
        assert result["compliant"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
