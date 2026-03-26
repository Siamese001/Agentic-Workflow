"""Tests for L5 Safety types."""

import re
from pathlib import Path

import pytest


class TestSafetyTypes:
    """Tests for safety type definitions."""

    def test_types_folder_exists(self):
        """Types folder should exist."""
        path = Path("agentic_core/L5_safety/types")
        assert path.exists(), "L5_safety/types/ should exist"

    def test_types_has_type_definitions(self):
        """Types folder should have type definition files."""
        types_path = Path("agentic_core/L5_safety/types")
        if types_path.exists():
            py_files = list(types_path.glob("*.py"))
            assert len(py_files) > 0, "L5_safety/types/ should have Python files"


class TestTypeFileNaming:
    """Tests for type file naming conventions."""

    def test_type_files_end_with_types(self):
        """Type files should end with _types.py."""
        types_path = Path("agentic_core/L5_safety/types")
        if not types_path.exists():
            pytest.fail("L5_safety/types/ not found")

        # Known legacy files that contain error/exception types but predate the _types convention
        KNOWN_EXCEPTIONS = {"hardening_errors.py"}
        non_types_files = []
        for py_file in types_path.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
            if py_file.name in KNOWN_EXCEPTIONS:
                continue
            if not py_file.stem.endswith("_types"):
                non_types_files.append(py_file.name)

        # This is a soft check - some files may have different naming
        if non_types_files:
            pytest.fail(f"Found {len(non_types_files)} files not ending in _types")


class TestTypeContentIntegrity:
    """Tests for type content integrity."""

    def test_no_agent_classes_in_types(self):
        """Type files should not contain Agent classes."""
        types_path = Path("agentic_core/L5_safety/types")
        if not types_path.exists():
            pytest.fail("L5_safety/types/ not found")

        violations = []
        for py_file in types_path.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            # Check for actual Agent class definitions (not instantiations)
            if re.search(r"^class \w+Agent[\ (]", content, re.MULTILINE):
                violations.append(py_file.name)

        # Note: Some legacy files may have embedded agents
        if violations:
            pytest.fail(f"Found {len(violations)} files with Agent classes (legacy)")

    def test_types_use_dataclass_or_typeddict(self):
        """Type files should use dataclass, TypedDict, or Protocol."""
        types_path = Path("agentic_core/L5_safety/types")
        if not types_path.exists():
            pytest.fail("L5_safety/types/ not found")

        type_patterns = ["@dataclass", "TypedDict", "Protocol", "Enum", "NamedTuple"]

        py_files = [f for f in types_path.glob("*.py") if not f.name.startswith("__")]