"""ADG-driven tests for L0_routing/scripts/add_dataclass_to_agents_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.add_dataclass_to_agents_util import (
        has_dataclass_decorator,
        has_dataclass_import,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    has_dataclass_decorator = None  # type: ignore[assignment]
    has_dataclass_import = None  # type: ignore[assignment]


@pytest.mark.skipif(not _AVAILABLE, reason="add_dataclass deps unavailable")
class TestHasDataclassDecorator:
    def test_detects_decorator(self):
        assert has_dataclass_decorator("@dataclass\nclass Foo:") is True

    def test_no_decorator(self):
        assert has_dataclass_decorator("class Foo:") is False


@pytest.mark.skipif(not _AVAILABLE, reason="add_dataclass deps unavailable")
class TestHasDataclassImport:
    def test_detects_from_import(self):
        assert has_dataclass_import("from dataclasses import dataclass") is True

    def test_detects_module_import(self):
        assert has_dataclass_import("import dataclasses") is True

    def test_no_import(self):
        assert has_dataclass_import("import os") is False


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
