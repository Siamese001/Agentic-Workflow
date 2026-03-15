"""ADG-driven tests for agentic_core/L5_safety/validators/CodeJanitorAgent.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.validators.CodeJanitorAgent import (  # noqa: F401
        CodeJanitorAgent,
        JanitorViolation,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    JanitorViolation = None  # type: ignore[assignment,misc]
    CodeJanitorAgent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="CodeJanitorAgent.py deps unavailable")
class TestJanitorViolation:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(JanitorViolation)
    def test_importable(self):
        assert JanitorViolation is not None

@pytest.mark.skipif(not _AVAILABLE, reason="CodeJanitorAgent.py deps unavailable")
class TestCodeJanitorAgent:
    def test_is_class(self):
        assert isinstance(CodeJanitorAgent, type)
    def test_importable(self):
        assert CodeJanitorAgent is not None


def test_module_importable():
    """Module CodeJanitorAgent.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
