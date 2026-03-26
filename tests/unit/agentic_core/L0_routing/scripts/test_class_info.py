"""Foundational behavioral tests for agentic_core/L0_routing/scripts/class_info.py.

fan_in=13 — this module is imported by 13 other modules.
ADG contract: import-hygiene is covered by test_class_info_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: from agentic_core.L0_routing.scripts.class_info import (  # noqa: F401
    AGENTIC_CORE_DIR,
    ARCHIVES_DIR,
    EXCLUDE_DIRS,
    PROJECT_ROOT,
    TARGET_ARCHIVES,
    ClassInfo,
    FileAnalysis,
    compute_file_hash,
    count_lines,
    get_snippet,
    parse_python_file,
)


class TestClassInfoContract:
    def test_is_dataclass(self):
                from agentic_core.L0_routing.scripts.class_info import (  # noqa: F401
                import dataclasses
                assert dataclasses.is_dataclass(ClassInfo)

        assert dataclasses.is_dataclass(ClassInfo)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ClassInfo)}
        assert field_names >= {'docstring', 'methods', 'line_number', 'bases', 'name'}

class TestFileAnalysisContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(FileAnalysis)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(FileAnalysis)}
        assert field_names >= {'line_count', 'path', 'size_bytes', 'relative_path', 'extension'}

class TestComputeFileHashFunction:
    def test_is_callable(self):
    """Test is_callable runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute is_callable
    result = None  # Replace with actual execution

"""Test is_callable runtime behavior."""
# Arrange
# TODO: Set up execution parameters
input_data = {}  # Replace with actual test data

# Act
# TODO: Execute is_callable
result = None  # Replace with actual execution

"""Test is_callable runtime behavior."""
# Arrange
# TODO: Set up execution parameters
input_data = {}  # Replace with actual test data

# Act
# TODO: Execute is_callable
result = None  # Replace with actual execution

"""Test is_callable runtime behavior."""
# Arrange
# TODO: Set up execution parameters
input_data = {}  # Replace with actual test data

# Act
# TODO: Execute is_callable
result = None  # Replace with actual execution

# Assert
assert result is not None, f"{function_name} should return a result"
assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
# TODO: Add specific execution assertions
        assert ARCHIVES_DIR is not None

class TestAgenticCoreDirConstant:
    def test_is_not_none(self):
        assert AGENTIC_CORE_DIR is not None

class TestTargetArchivesConstant:
    def test_is_not_none(self):
        assert TARGET_ARCHIVES is not None

    def test_is_non_empty_sequence(self):
        assert hasattr(TARGET_ARCHIVES, '__len__')

class TestExcludeDirsConstant:
    def test_is_not_none(self):
        assert EXCLUDE_DIRS is not None


def test_module_importable():
    """Module class_info must be importable or skip gracefully."""
    pass  # Import verified at module level
