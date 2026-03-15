#!/usr/bin/env python3
"""
Guardian Test for Architecture Governance
Comprehensive tests for layer boundaries, naming conventions, and structural compliance.

Merged from:
- test_architecture_governance.py (core validation logic)
- test_architecture_governance_comprehensive.py (test cases)
"""

import ast
import shutil
import sys
from pathlib import Path
from typing import Any

import pytest

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

LAYER_HIERARCHY = {
    "L0_routing": 0,
    "L1_cognition": 1,
    "L2_execution": 2,
    "L3_orchestration": 3,
    "L4_state": 4,
    "L5_safety": 5,
    "L6_observability": 6,
}


class ArchitectureGovernanceValidator:
    """Validates architecture governance including layer boundaries and naming."""

    @staticmethod
    def get_layer_from_path(file_path: Path) -> tuple[str, int]:
        """Extract layer from file path."""
        parts = file_path.parts
        for part in parts:
            if part in LAYER_HIERARCHY:
                return (part, LAYER_HIERARCHY[part])
        return ("unknown", -1)

    @staticmethod
    def check_gravity_violations(file_path: Path) -> list[str]:
        """Check for gravity violations (lower layers importing from higher layers)."""
        violations = []

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(content)

            current_layer, current_level = ArchitectureGovernanceValidator.get_layer_from_path(file_path)

            if current_level == -1:
                return []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import | ast.ImportFrom):
                    if isinstance(node, ast.ImportFrom) and node.module:
                        module_parts = node.module.split(".")

                        if len(module_parts) >= 2 and module_parts[0] == AGENTIC_CORE_DIR:
                            imported_layer = module_parts[1]
                            if imported_layer in LAYER_HIERARCHY:
                                imported_level = LAYER_HIERARCHY[imported_layer]

                                if current_level < imported_level:
                                    violations.append(
                                        f"Gravity violation: {current_layer} (L{current_level}) "
                                        f"importing from {imported_layer} (L{imported_level})",
                                    )
        except (OSError, UnicodeDecodeError, SyntaxError) as e:
            violations.append(f"Error parsing file: {e}")

        return violations

    @staticmethod
    def check_naming_convention(file_path: Path) -> list[str]:
        """Check that agent files follow naming conventions."""
        violations = []

        if AGENTIC_CORE_DIR not in str(file_path):
            return []

        if file_path.suffix != ".py":
            return []

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(content)

            agent_classes = [
                node.name
                for node in ast.walk(tree)
                if isinstance(node, ast.ClassDef) and node.name.endswith("Agent")
            ]

            if agent_classes and not file_path.stem.endswith("Agent"):
                violations.append(
                    f"Naming violation: File contains agent classes {agent_classes} "
                    f"but doesn't end with 'Agent.py'",
                )
        except (OSError, UnicodeDecodeError, SyntaxError):
            pass

        return violations

    @staticmethod
    def validate_file(file_path: Path) -> dict[str, Any]:
        """Validate a file for architecture governance."""
        result = {
            "compliant": True,
            "gravity_violations": [],
            "naming_violations": [],
            "error": None,
        }

        if not file_path.exists():
            result["error"] = f"File does not exist: {file_path}"
            result["compliant"] = False
            return result

        if not file_path.is_file():
            result["error"] = f"Not a file: {file_path}"
            result["compliant"] = False
            return result

        result["gravity_violations"] = ArchitectureGovernanceValidator.check_gravity_violations(file_path)
        result["naming_violations"] = ArchitectureGovernanceValidator.check_naming_convention(file_path)

        if result["gravity_violations"] or result["naming_violations"]:
            result["compliant"] = False

        return result


class TestArchitectureGovernance:
    """Comprehensive architecture governance tests."""

    @pytest.fixture
    def validator(self):
        """Provide validator instance."""
        return ArchitectureGovernanceValidator()

    @pytest.fixture
    def temp_agentic_core(self, tmp_path):
        """Create temporary agentic_core structure."""
        base = tmp_path / "temp_test_agentic_core"
        base.mkdir()
        yield base
        shutil.rmtree(base, ignore_errors=True)

    def _create_layer_file(self, temp_base: Path, layer: str, filename: str, code: str) -> Path:
        """Create a file in a specific layer."""
        layer_dir = temp_base / layer
        layer_dir.mkdir(parents=True, exist_ok=True)
        file_path = layer_dir / filename
        file_path.write_text(code)
        return file_path

    def test_compliant_file_passes(self, validator, temp_agentic_core):
        """TC-AG-01: Compliant file with no violations passes."""
        agent_code = """
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

class TestAgent(SovereignBaseAgent):
    def run(self):
        pass
"""
        temp_file = self._create_layer_file(temp_agentic_core, "L5_safety", "TestAgent.py", agent_code)

        result = validator.validate_file(temp_file)
        assert result["compliant"], f"Expected compliant, got: {result}"

    def test_gravity_violation_detected(self, validator, temp_agentic_core):
        """TC-AG-02: Gravity violation (lower layer importing higher) detected."""
        agent_code = """
from agentic_core.L5_safety.validators.SomeValidator import SomeValidator

class CognitionAgent:
    def run(self):
        pass
"""
        temp_file = self._create_layer_file(
            temp_agentic_core,
            "L1_cognition",
            "CognitionAgent.py",
            agent_code,
        )

        result = validator.validate_file(temp_file)
        assert not result["compliant"]
        assert any("Gravity violation" in v for v in result["gravity_violations"])

    def test_naming_convention_violation(self, validator, temp_agentic_core):
        """TC-AG-03: Agent class in file not ending with Agent.py."""
        agent_code = """
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

class TestAgent(SovereignBaseAgent):
    def run(self):
        pass
"""
        temp_file = self._create_layer_file(temp_agentic_core, "L5_safety", "test_file.py", agent_code)

        result = validator.validate_file(temp_file)
        assert not result["compliant"]
        assert any("Naming violation" in v for v in result["naming_violations"])

    def test_nonexistent_file(self, validator):
        """TC-AG-04: Nonexistent file fails."""
        result = validator.validate_file(Path("nonexistent_file.py"))
        assert result["error"] is not None
        assert "does not exist" in result["error"]

    def test_valid_upward_import(self, validator, temp_agentic_core):
        """TC-AG-05: Valid upward import (higher layer importing lower) passes."""
        agent_code = """
from agentic_core.L1_cognition.engines.CognitiveNode import CognitiveNode

class SafetyAgent:
    def run(self):
        pass
"""
        temp_file = self._create_layer_file(temp_agentic_core, "L5_safety", "SafetyAgent.py", agent_code)

        result = validator.validate_file(temp_file)
        assert result["compliant"]

    def test_non_agent_file_passes(self, validator, temp_agentic_core):
        """TC-AG-06: Non-agent utility file passes."""
        util_code = """
def helper_function():
    return True

class UtilityClass:
    pass
"""
        temp_file = self._create_layer_file(temp_agentic_core, "L5_safety", "utils.py", util_code)

        result = validator.validate_file(temp_file)
        assert result["compliant"]

    def test_syntax_error_handling(self, validator, temp_agentic_core):
        """TC-AG-07: Syntax errors handled gracefully."""
        agent_code = """
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

class TestAgent(SovereignBaseAgent):
    def run(self):
        bad_string = "unclosed
        pass
"""
        temp_file = self._create_layer_file(temp_agentic_core, "L5_safety", "TestAgent.py", agent_code)

        validator.validate_file(temp_file)
        # Should handle gracefully without crashing

    def test_multiple_violations(self, validator, temp_agentic_core):
        """TC-AG-08: Multiple violations detected in single file."""
        agent_code = """
from agentic_core.L6_observability.dashboard import Dashboard
from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    AGENTIC_CORE_DIR,
)

class TestAgent:
    def run(self):
        pass
"""
        temp_file = self._create_layer_file(temp_agentic_core, "L1_cognition", "test_file.py", agent_code)

        result = validator.validate_file(temp_file)
        assert not result["compliant"]
        # Should detect at least one type of violation
        has_violation = bool(result["gravity_violations"]) or bool(result["naming_violations"])
        assert has_violation


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
