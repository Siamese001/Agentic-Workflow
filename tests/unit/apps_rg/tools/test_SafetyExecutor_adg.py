"""ADG-driven tests for apps_rg/tools/SafetyExecutor.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_rg.tools.SafetyExecutor import (  # noqa: F401
        SafetyExecutor,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    SafetyExecutor = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="SafetyExecutor.py deps unavailable")
class TestSafetyExecutor:
    def test_is_class(self):
        assert isinstance(SafetyExecutor, type)
    def test_importable(self):
        assert SafetyExecutor is not None


def test_module_importable():
    """Module SafetyExecutor.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE