"""Tests for L5 Safety types."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

TYPES_PATH = Path("agentic_core/L5_safety/types")


def _require_types_path() -> Path:
    if not TYPES_PATH.exists():
        pytest.skip("Standalone snapshot does not include agentic_core/L5_safety/types.")
    return TYPES_PATH


class TestSafetyTypes:
    def test_types_folder_exists(self):
        assert _require_types_path().exists()

    def test_types_has_type_definitions(self):
        py_files = list(_require_types_path().glob("*.py"))
        assert len(py_files) > 0, "L5_safety/types/ should have Python files"


class TestTypeFileNaming:
    def test_type_files_end_with_types(self):
        types_path = _require_types_path()
        known_exceptions = {"hardening_errors.py"}
        non_types_files = []
        for py_file in types_path.glob("*.py"):
            if py_file.name.startswith("__") or py_file.name in known_exceptions:
                continue
            if not py_file.stem.endswith("_types"):
                non_types_files.append(py_file.name)
        if non_types_files:
            pytest.fail(f"Found {len(non_types_files)} files not ending in _types")


class TestTypeContentIntegrity:
    def test_no_agent_classes_in_types(self):
        types_path = _require_types_path()
        violations = []
        for py_file in types_path.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"^class \w+Agent[\ (]", content, re.MULTILINE):
                violations.append(py_file.name)
        if violations:
            pytest.fail(f"Found {len(violations)} files with Agent classes (legacy)")

    def test_types_use_dataclass_or_typeddict(self):
        types_path = _require_types_path()
        type_patterns = ["@dataclass", "TypedDict", "Protocol", "Enum", "NamedTuple"]
        py_files = [f for f in types_path.glob("*.py") if not f.name.startswith("__")]
        assert py_files, "Expected at least one type module to scan"
        assert any(
            any(pattern in py_file.read_text(encoding="utf-8", errors="ignore") for pattern in type_patterns)
            for py_file in py_files
        )
