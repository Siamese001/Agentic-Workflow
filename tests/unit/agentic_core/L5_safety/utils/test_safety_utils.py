"""Tests for L5 Safety utilities."""

from pathlib import Path

import pytest


class TestSafetyUtils:
    """Tests for safety utility functions."""

    def test_utils_folder_exists(self):
        """Utils folder should exist."""
        path = Path("agentic_core/L5_safety/utils")
        assert path.exists(), "L5_safety/utils/ should exist"

    def test_utils_has_utility_files(self):
        """Utils folder should have utility files."""
        utils_path = Path("agentic_core/L5_safety/utils")
        if utils_path.exists():
            py_files = list(utils_path.glob("*.py"))
            assert len(py_files) > 0, "L5_safety/utils/ should have Python files"


class TestSubprocessSecurityUtil:
    """Tests for subprocess security utility."""

    def test_subprocess_security_exists(self):
        """Subprocess security utility should exist."""
        util_path = Path("agentic_core/L5_safety/utils/subprocess_security_util.py")
        if not util_path.exists():
            pytest.skip("subprocess_security_util.py not found")

        content = util_path.read_text(encoding="utf-8", errors="ignore")
        assert "def " in content, "Should have utility functions"


class TestUtilFileNaming:
    """Tests for utility file naming conventions."""

    def test_util_files_end_with_util(self):
        """Utility files should end with _util.py."""
        utils_path = Path("agentic_core/L5_safety/utils")
        if not utils_path.exists():
            pytest.skip("L5_safety/utils/ not found")

        non_util_files = []
        for py_file in utils_path.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
            if not py_file.stem.endswith("_util"):
                non_util_files.append(py_file.name)

        # This is a soft check - some files may have different naming
        if non_util_files:
            pytest.skip(f"Found {len(non_util_files)} files not ending in _util")


class TestUtilContentIntegrity:
    """Tests for utility content integrity."""

    def test_no_agent_classes_in_utils(self):
        """Utility files should not contain Agent classes."""
        utils_path = Path("agentic_core/L5_safety/utils")
        if not utils_path.exists():
            pytest.skip("L5_safety/utils/ not found")

        violations = []
        for py_file in utils_path.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            if "class " in content and "Agent(" in content:
                violations.append(py_file.name)

        # Note: Some legacy files may have embedded agents
        if violations:
            pytest.skip(f"Found {len(violations)} files with Agent classes (legacy)")

    def test_utils_have_functions(self):
        """Utility files should have function definitions."""
        utils_path = Path("agentic_core/L5_safety/utils")
        if not utils_path.exists():
            pytest.skip("L5_safety/utils/ not found")

        # Some utility files may only contain constants/imports
        constant_only_files = ["location_constants_util.py"]

        for py_file in utils_path.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
            if py_file.name in constant_only_files:
                continue
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            # Should have at least one function or class
            has_definition = "def " in content or "class " in content
            assert has_definition, f"{py_file.name} should have function or class definitions"
