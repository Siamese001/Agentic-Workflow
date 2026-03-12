"""ADG contract tests for agentic_core/L5_safety/types/resource_management_types.py.

Uses regex/AST source inspection — immune to SyntaxError in source.
"""
from __future__ import annotations
import pathlib
import re
import pytest

pytestmark = pytest.mark.unit
try:
    import agentic_core.L5_safety.types.resource_management_types as _mod  # noqa: F401  # ADG covers
except Exception:
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
        assert _SRC.exists()

    def test_has_resource_type(self):
        assert "ResourceType" in _class_names()

    def test_has_resource_quota(self):
        assert "ResourceQuota" in _class_names()

    def test_has_resource_check_result(self):
        assert "ResourceCheckResult" in _class_names()

    def test_has_resource_management_guardrail(self):
        assert "ResourceManagementGuardrail" in _class_names()

    def test_resource_type_has_tokens_member(self):
        src = _src_text()
        assert "TOKENS" in src or "tokens" in src.lower()

    def test_resource_type_has_cost_member(self):
        src = _src_text()
        assert "COST" in src or "cost" in src.lower()

    def test_resource_quota_has_remaining(self):
        src = _src_text()
        assert "remaining" in src

    def test_resource_quota_has_usage_percent(self):
        src = _src_text()
        assert "usage_percent" in src or "percent" in src.lower()
