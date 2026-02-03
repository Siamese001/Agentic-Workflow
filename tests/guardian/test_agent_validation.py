#!/usr/bin/env python3
"""
Guardian Test for Agent Validation
Comprehensive tests for agent structure and compliance validation.

Merged from:
- test_agent_validation.py (core validation logic)
- test_agent_validation_comprehensive.py (test cases)
"""

import ast
import sys
import tempfile
from pathlib import Path
from typing import Any

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class AgentStructureValidator:
    """Validates agent structure using static analysis."""

    @staticmethod
    def check_agent_structure(file_path: Path) -> dict[str, Any]:
        """
        Check agent structure using static analysis.

        Returns:
            Dict with validation results
        """
        results = {
            "has_agent_class": False,
            "has_init": False,
            "has_run_method": False,
            "has_heal_method": False,
            "has_test_method": False,
            "violations": [],
            "error": None,
        }

        if not file_path.exists():
            results["error"] = f"File does not exist: {file_path}"
            return results

        if not file_path.is_file():
            results["error"] = f"Not a file: {file_path}"
            return results

        if file_path.suffix != ".py":
            results["error"] = f"Not a Python file: {file_path}"
            return results

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(content)

            agent_classes = [
                node
                for node in ast.walk(tree)
                if isinstance(node, ast.ClassDef) and node.name.endswith("Agent")
            ]

            if not agent_classes:
                results["violations"].append("No agent classes found")
                return results

            results["has_agent_class"] = True

            agent_class = agent_classes[0]
            methods = [node.name for node in agent_class.body if isinstance(node, ast.FunctionDef)]

            if "__init__" in methods or "__post_init__" in methods:
                results["has_init"] = True

            if "run" in methods:
                results["has_run_method"] = True

            if "heal" in methods or "heal_repository" in methods or "apply_fix" in methods:
                results["has_heal_method"] = True

            if any(m.startswith("test_") or "self_test" in m for m in methods):
                results["has_test_method"] = True

        except SyntaxError as e:
            results["violations"].append(f"Syntax error: {e}")
        except Exception as e:
            results["violations"].append(f"Error parsing file: {e}")

        return results

    @staticmethod
    def is_compliant(results: dict[str, Any]) -> bool:
        """Check if results indicate compliance."""
        if results.get("error"):
            return False
        if results["violations"]:
            return False
        if not results["has_agent_class"]:
            return False
        return True


class TestAgentValidation:
    """Comprehensive agent validation tests."""

    @pytest.fixture
    def validator(self):
        """Provide validator instance."""
        return AgentStructureValidator()

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
            except PermissionError:
                time.sleep(0.1)

    def test_valid_agent_passes(self, validator):
        """TC-AV-01: Valid agent with all methods passes."""
        agent_code = """
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

class TestAgent(SovereignBaseAgent):
    def __init__(self):
        pass

    def run(self):
        pass

    def heal_repository(self):
        pass

    def test_self(self):
        pass
"""
        temp_path = self._create_temp_file(agent_code, suffix="Agent.py")
        try:
            results = validator.check_agent_structure(temp_path)
            assert validator.is_compliant(results)
            assert results["has_agent_class"]
            assert results["has_init"]
            assert results["has_run_method"]
            assert results["has_heal_method"]
            assert results["has_test_method"]
        finally:
            self._cleanup_temp_file(temp_path)

    def test_agent_without_init(self, validator):
        """TC-AV-02: Agent without __init__ still passes (dataclass pattern)."""
        agent_code = """
from dataclasses import dataclass

@dataclass
class TestAgent:
    def run(self):
        pass
"""
        temp_path = self._create_temp_file(agent_code, suffix="Agent.py")
        try:
            results = validator.check_agent_structure(temp_path)
            assert validator.is_compliant(results)
            assert results["has_agent_class"]
        finally:
            self._cleanup_temp_file(temp_path)

    def test_no_agent_class_fails(self, validator):
        """TC-AV-03: File without agent class fails."""
        code = """
class UtilityClass:
    pass

def some_function():
    pass
"""
        temp_path = self._create_temp_file(code)
        try:
            results = validator.check_agent_structure(temp_path)
            assert not validator.is_compliant(results)
            assert "No agent classes found" in results["violations"]
        finally:
            self._cleanup_temp_file(temp_path)

    def test_syntax_error_fails(self, validator):
        """TC-AV-04: File with syntax error fails."""
        agent_code = """
class TestAgent:
    def run(self):
        bad_string = "unclosed
        pass
"""
        temp_path = self._create_temp_file(agent_code, suffix="Agent.py")
        try:
            results = validator.check_agent_structure(temp_path)
            assert not validator.is_compliant(results)
            assert any("Syntax error" in v for v in results["violations"])
        finally:
            self._cleanup_temp_file(temp_path)

    def test_nonexistent_file_fails(self, validator):
        """TC-AV-05: Nonexistent file fails."""
        results = validator.check_agent_structure(Path("nonexistent_agent.py"))
        assert results["error"] is not None
        assert "does not exist" in results["error"]

    def test_non_python_file_fails(self, validator):
        """TC-AV-06: Non-Python file fails."""
        temp_path = self._create_temp_file("Not a Python file", suffix=".txt")
        try:
            results = validator.check_agent_structure(temp_path)
            assert results["error"] is not None
            assert "Not a Python file" in results["error"]
        finally:
            self._cleanup_temp_file(temp_path)

    def test_multiple_agent_classes(self, validator):
        """TC-AV-07: File with multiple agent classes validates first one."""
        agent_code = """
class FirstAgent:
    def run(self):
        pass

class SecondAgent:
    def run(self):
        pass
"""
        temp_path = self._create_temp_file(agent_code, suffix="Agent.py")
        try:
            results = validator.check_agent_structure(temp_path)
            assert validator.is_compliant(results)
            assert results["has_agent_class"]
        finally:
            self._cleanup_temp_file(temp_path)

    def test_minimal_agent_passes(self, validator):
        """TC-AV-08: Minimal agent with just class definition passes."""
        agent_code = """
class MinimalAgent:
    pass
"""
        temp_path = self._create_temp_file(agent_code, suffix="Agent.py")
        try:
            results = validator.check_agent_structure(temp_path)
            assert validator.is_compliant(results)
            assert results["has_agent_class"]
        finally:
            self._cleanup_temp_file(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
