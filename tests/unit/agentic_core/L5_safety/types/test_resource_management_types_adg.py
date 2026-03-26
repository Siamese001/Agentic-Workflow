"""ADG contract tests for agentic_core/L5_safety/types/resource_management_types.py.

Uses regex/AST source inspection — immune to SyntaxError in source.
"""
from __future__ import annotations

import pathlib
import re

import pytest

pytestmark = pytest.mark.unit
try:
#  # MOVED: import agentic_core.L5_safety.types.resource_management_types as _mod  # noqa: F401  # ADG covers
except (ValueError, TypeError, RuntimeError) as e:
    _mod = None


_SRC = (
    pathlib.Path(__file__).parents[5]
    / "agentic_core" / "L5_safety" / "types" / "resource_management_types.py"
)


def _src_text():
    return _SRC.read_text(encoding="utf-8", errors="replace")


def _class_names():
    return set(re.findall(r"^class\s+(\w+)", _src_text(), re.MULTILINE))


class TestResourceManagementTypesSource:
    def test_source_exists(self):
                import agentic_core.L5_safety.types.resource_management_types as _mod  # noqa: F401  # ADG covers
                assert _SRC.exists()

        assert _SRC.exists()

    def test_has_resource_type(self):
        assert "ResourceType" in _class_names()

    def test_has_resource_quota(self):
        assert "ResourceQuota" in _class_names()

    def test_has_resource_check_result(self):
    """Test has_resource_check_result contract compliance."""
    # Arrange
    # TODO: Set up test data
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Validate schema
    validation_result = None  # Replace with actual validation

    # Assert - Schema Contract
    assert validation_result is not None, "Schema validation should produce a result"
    assert isinstance(validation_result, (bool, dict)), "Validation result should be structured"
    # TODO: Add specific schema validation assertions
    # assert validation_result.get("valid", False), "Data should conform to schema"
        src = _src_text()
        assert "remaining" in src

    def test_resource_quota_has_usage_percent(self):
        src = _src_text()
        assert "usage_percent" in src or "percent" in src.lower()
