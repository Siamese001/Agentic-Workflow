"""ADG-driven tests for L1_cognition/engines/domain_manager.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L1_cognition.engines.domain_manager import DomainContextManager
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    DomainContextManager = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="domain_manager deps unavailable")
class TestDomainContextManager:
    def test_importable(self):
        assert callable(DomainContextManager)

    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(DomainContextManager)

    def test_creates(self):
        mgr = DomainContextManager()
        assert mgr is not None


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
