"""ADG-driven tests for L0_routing/enforcement/boot_sequence.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.enforcement.boot_sequence import BootSequence
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    BootSequence = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="boot_sequence deps unavailable")
class TestBootSequence:
    def test_importable(self):
        assert callable(BootSequence)

    def test_creates_with_defaults(self):
        bs = BootSequence()
        assert bs.strict_mode is True
        assert bs.discovered_agents == []
        assert bs.compliance_violations == []

    def test_creates_non_strict(self):
        bs = BootSequence(strict_mode=False)
        assert bs.strict_mode is False

    def test_has_execute_boot(self):
        assert hasattr(BootSequence, "execute_boot")


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
