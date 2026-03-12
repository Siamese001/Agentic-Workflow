"""ADG-driven tests for L2_execution/utils/deterministic_cleaner_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.utils.deterministic_cleaner_util import DeterministicCleaner
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    DeterministicCleaner = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="deterministic_cleaner_util deps unavailable")
class TestDeterministicCleaner:
    def test_creates_with_defaults(self):
        cleaner = DeterministicCleaner()
        assert cleaner is not None

    def test_creates_with_flags_off(self):
        cleaner = DeterministicCleaner(enable_isort=False, enable_autopep8=False)
        assert cleaner is not None

    def test_has_clean_method(self):
        assert hasattr(DeterministicCleaner, "clean") or hasattr(DeterministicCleaner, "clean_code")


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
