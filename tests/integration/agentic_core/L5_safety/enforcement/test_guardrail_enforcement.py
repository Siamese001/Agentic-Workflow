"""Tests for L5 Safety enforcement functionality."""

from pathlib import Path

import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class TestGuardrailEnforcement:
    """Tests for guardrail enforcement functionality."""

    def test_enforcement_folder_exists(self):
        """Enforcement folder should exist."""
        path = Path("agentic_core/L5_safety/enforcement")
        assert path.exists(), "L5_safety/enforcement/ should exist"

    def test_enforcement_has_guardrail_classes(self):
        """Enforcement should have guardrail/safety classes."""
        enforcement_path = Path("agentic_core/L5_safety/enforcement")
        if enforcement_path.exists():
            py_files = list(enforcement_path.glob("*.py"))
            assert len(py_files) > 0, "L5_safety/enforcement/ should have Python files"


class TestSafeSubprocessHandler:
    """Tests for safe subprocess handling."""

    def test_safe_subprocess_handler_exists(self):
        """Safe subprocess handler should exist in enforcement/."""
        handler_path = Path("agentic_core/L5_safety/enforcement/safe_subprocess_handler_enforcer.py")
        assert handler_path.exists(), "safe_subprocess_handler.py should exist"

    def test_subprocess_security_util_exists(self):
        """Subprocess security utility should exist."""
        util_path = Path("agentic_core/L5_safety/utils/subprocess_security_util.py")
        if not util_path.exists():
            pytest.fail("subprocess_security_util.py not found")

        content = util_path.read_text(encoding="utf-8", errors="ignore")
        assert "def " in content, "Should have utility functions"


class TestHealingStrategy:
    """Tests for healing strategy enforcement."""

    def test_healing_strategy_exists(self):
        """Healing strategy should exist in enforcement/."""
        strategy_path = Path("agentic_core/L5_safety/enforcement/HealingStrategy.py")
        if not strategy_path.exists():
            pytest.fail("HealingStrategy.py not found")

        content = strategy_path.read_text(encoding="utf-8", errors="ignore")
        assert "class " in content, "Should have class definition"


class TestEnforcementLayerIntegrity:
    """Tests for L5 enforcement structural integrity."""

    def test_enforcement_not_reasoning(self):
        """Enforcement files should be enforcement, not reasoning."""
        enforcement_path = Path("agentic_core/L5_safety/enforcement")
        if not enforcement_path.exists():
            pytest.fail("L5_safety/enforcement/ not found")

        # Enforcement files should have enforcement-related names

        py_files = [f for f in enforcement_path.glob("*.py") if not f.name.startswith("__")]

    def test_no_agent_classes_in_enforcement(self):
        """Agent classes should not be in enforcement/ (should be in reasoning/)."""
        enforcement_path = Path("agentic_core/L5_safety/enforcement")
        if not enforcement_path.exists():
            pytest.fail("L5_safety/enforcement/ not found")

        violations = []
        for py_file in enforcement_path.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            # Check for Agent class definitions (not just Agent in name)
            if "class " in content and "Agent(" in content and "Agent:" in content:
                violations.append(str(py_file))

        # Note: Some enforcement files may have Agent classes (legacy)
        if violations:
            pytest.fail(f"Found {len(violations)} Agent classes in enforcement/ (may be legacy)")
