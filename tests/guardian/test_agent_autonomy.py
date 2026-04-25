#!/usr/bin/env python3
"""
Guardian Test for Agent Autonomy Compliance
Comprehensive tests for agent autonomy methods and compliance validation.

Merged from:
- test_agent_autonomy.py (core validation logic)
- test_agent_autonomy_comprehensive.py (test cases)
"""

import ast
import sys
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

REQUIRED_METHODS = ["heal_repository"]


class AgentAutonomyValidator:
    """Validates agent autonomy compliance using AST analysis."""

    @staticmethod
    def validate_agent_file(agent_file: Path) -> dict:
        """
        Validate an agent file for autonomy compliance.

        Returns:
            Dict with 'compliant' bool, 'violations' list, 'error' optional str
        """
        result = {"compliant": False, "violations": [], "error": None}

        if not agent_file.exists():
            result["error"] = f"Agent file does not exist: {agent_file}"
            return result

        if agent_file.suffix != ".py":
            result["error"] = f"Not a Python file: {agent_file}"
            return result

        try:
            content = agent_file.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(content)

            agent_classes = [
                node
                for node in ast.walk(tree)
                if isinstance(node, ast.ClassDef) and node.name.endswith("Agent")
            ]

            if not agent_classes:
                result["error"] = f"No agent classes found in {agent_file}"
                return result

            for class_node in agent_classes:
                method_names = {
                    node.name for node in ast.walk(class_node) if isinstance(node, ast.FunctionDef)
                }

                missing_methods = [method for method in REQUIRED_METHODS if method not in method_names]

                if missing_methods:
                    result["violations"].append(f"{class_node.name}: missing {', '.join(missing_methods)}")

            result["compliant"] = len(result["violations"]) == 0

        except SyntaxError as e:  # review: Syntax errors should be caught at parser level, not runtime
            result["error"] = f"Syntax error in {agent_file}: {e}"
        except (OSError, UnicodeDecodeError, AttributeError) as e:
            result["error"] = f"Error processing {agent_file}: {e}"

        return result


class TestAgentAutonomy:
    """Comprehensive agent autonomy compliance tests."""

    @pytest.fixture
    def validator(self):
        """Provide validator instance."""
        return AgentAutonomyValidator()

    def _create_temp_file(self, code: str, suffix: str = ".py") -> Path:
        """Create a temporary file with given code."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False) as f:
            f.write(code)
            f.flush()
            return Path(f.name)

    def _cleanup_temp_file(self, temp_path: Path) -> None:
        """Clean up temporary file with retry for Windows."""
        import time

        for _ in range(3):
            try:
                temp_path.unlink(missing_ok=True)
                break
            except PermissionError:  # review: Permission errors should validate access before operation
                time.sleep(0.1)

    def test_agent_with_heal_repository(self, validator):
        """TC-AA-01: Agent with heal_repository passes."""
        agent_code = """
class TestAgent:
    def heal_repository(self):
        pass
"""
        temp_path = self._create_temp_file(agent_code)
        try:
            result = validator.validate_agent_file(temp_path)
            assert result["compliant"], f"Expected compliant, got violations: {result['violations']}"
            assert not result["error"]
        finally:
            self._cleanup_temp_file(temp_path)

    def test_agent_missing_heal_repository(self, validator):
        """TC-AA-02: Agent missing heal_repository fails."""
        agent_code = """
class TestAgent:
    def some_other_method(self):
        pass
"""
        temp_path = self._create_temp_file(agent_code)
        try:
            result = validator.validate_agent_file(temp_path)
            assert not result["compliant"]
            assert any("missing heal_repository" in v for v in result["violations"])
        finally:
            self._cleanup_temp_file(temp_path)

    def test_nonexistent_file(self, validator):
        """TC-AA-03: Nonexistent file fails."""
        result = validator.validate_agent_file(Path("nonexistent_agent.py"))
        assert result["error"] is not None
        assert "does not exist" in result["error"]

    def test_syntax_error_file(self, validator):
        """TC-AA-04: File with syntax error fails."""
        agent_code = """
class TestAgent:
    def heal_repository(self):
        bad_string = "unclosed string
        pass
"""
        temp_path = self._create_temp_file(agent_code)
        try:
            result = validator.validate_agent_file(temp_path)
            assert result["error"] is not None
            assert "Syntax error" in result["error"]
        finally:
            self._cleanup_temp_file(temp_path)

    def test_multiple_agent_classes(self, validator):
        """TC-AA-05: Multiple agent classes all checked."""
        agent_code = """
class TestAgent1:
    def heal_repository(self):
        pass

class TestAgent2:
    def heal_repository(self):
        pass

class AnotherAgent:
    def heal_repository(self):
        pass
"""
        temp_path = self._create_temp_file(agent_code)
        try:
            result = validator.validate_agent_file(temp_path)
            assert result["compliant"], f"Expected compliant, got violations: {result['violations']}"
        finally:
            self._cleanup_temp_file(temp_path)

    def test_no_agent_classes(self, validator):
        """TC-AA-06: File with no agent classes fails."""
        agent_code = """
class NotAnAgentClass:
    pass

def some_function():
    pass
"""
        temp_path = self._create_temp_file(agent_code)
        try:
            result = validator.validate_agent_file(temp_path)
            assert result["error"] is not None
            assert "No agent classes found" in result["error"]
        finally:
            self._cleanup_temp_file(temp_path)

    def test_partial_compliance(self, validator):
        """TC-AA-07: One agent compliant, one not."""
        agent_code = """
class CompliantAgent:
    def heal_repository(self):
        pass

class NonCompliantAgent:
    def some_other_method(self):
        pass
"""
        temp_path = self._create_temp_file(agent_code)
        try:
            result = validator.validate_agent_file(temp_path)
            assert not result["compliant"]
            assert any(
                "NonCompliantAgent" in v and "missing heal_repository" in v for v in result["violations"]
            )
        finally:
            self._cleanup_temp_file(temp_path)

    def test_non_python_file(self, validator):
        """TC-AA-08: Non-Python file fails."""
        temp_path = self._create_temp_file("Not a Python file", suffix=".txt")
        try:
            result = validator.validate_agent_file(temp_path)
            assert result["error"] is not None
            assert "Not a Python file" in result["error"]
        finally:
            self._cleanup_temp_file(temp_path)


def test_required_methods() -> None:
    """
    Test that agent files have required autonomy methods.

    This test is currently disabled as heal_repository is not universally
    required for all agents. It's only required for agents that inherit
    from HealingPolicyMixin.
    """
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
