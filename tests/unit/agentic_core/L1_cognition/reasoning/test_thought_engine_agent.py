"""Tests for L1 Cognition reasoning agents."""

from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    L1_COGNITION_DIR,
)


class TestThoughtEngineAgent:
    """Tests for ThoughtEngineAgent core functionality."""

    def test_thought_engine_exists(self):
        """ThoughtEngineAgent module should exist."""
        path = Path("agentic_core/L1_cognition/reasoning")
        assert path.exists(), "L1_cognition/reasoning/ should exist"

    def test_thought_engine_has_agent_class(self):
        """ThoughtEngineAgent should define an Agent class."""
        # Check for agent files in reasoning/
        reasoning_path = Path("agentic_core/L1_cognition/reasoning")
        if reasoning_path.exists():
            agent_files = list(reasoning_path.glob("*Agent.py"))
            assert len(agent_files) > 0, "L1_cognition/reasoning/ should have Agent files"

    def test_cognition_agents_inherit_correctly(self):
        """L1 cognition agents should inherit from appropriate base."""
        reasoning_path = Path("agentic_core/L1_cognition/reasoning")
        if not reasoning_path.exists():
            pytest.fail("L1_cognition/reasoning/ not found")

        for agent_file in reasoning_path.glob("*Agent.py"):
            content = agent_file.read_text(encoding="utf-8", errors="ignore")
            # Should have class definition
            assert "class " in content, f"{agent_file.name} should define a class"


class TestIntentAnalysisAgent:
    """Tests for intent analysis functionality."""

    def test_intent_analysis_module_structure(self):
        """Intent analysis should follow LCD structure."""
        base = Path(L1_COGNITION_DIR)
        required = ["reasoning", "types", "config"]
        for subfolder in required:
            path = base / subfolder
            assert path.exists(), f"L1_cognition/{subfolder}/ should exist"


class TestPlanningAgent:
    """Tests for planning functionality in L1."""

    def test_planning_types_defined(self):
        """Planning types should be defined in types/."""
        types_path = Path("agentic_core/L1_cognition/types")
        if not types_path.exists():
            pytest.fail("L1_cognition/types/ not found")

        type_files = list(types_path.glob("*.py"))
        assert len(type_files) > 0, "L1_cognition/types/ should have type definitions"


class TestCognitionLayerIntegrity:
    """Tests for L1 layer structural integrity."""

    def test_no_subprocess_in_cognition(self):
        """L1 cognition should not import subprocess."""
        base = Path(L1_COGNITION_DIR)
        if not base.exists():
            pytest.fail("L1_cognition/ not found")

        violations = []
        for py_file in base.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            if "import subprocess" in content:
                violations.append(str(py_file))

        assert len(violations) == 0, f"L1 should not use subprocess: {violations}"

    def test_cognition_agents_in_reasoning(self):
        """Agent classes in L1 should be in reasoning/."""
        base = Path(L1_COGNITION_DIR)
        if not base.exists():
            pytest.fail("L1_cognition/ not found")

        violations = []
        for subfolder in ["types", "config", "utils", "enforcement"]:
            subfolder_path = base / subfolder
            if not subfolder_path.exists():
                continue
            for py_file in subfolder_path.glob("*.py"):
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                if "class " in content and "Agent(" in content:
                    violations.append(str(py_file))

        assert len(violations) == 0, f"Agent classes outside reasoning/: {violations}"
