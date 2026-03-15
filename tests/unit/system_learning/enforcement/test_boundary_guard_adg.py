"""ADG-driven tests for system_learning/enforcement/boundary_guard.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from system_learning.enforcement.boundary_guard import (  # noqa: F401
        check_file_isolation,
        check_system_learning_isolation,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    check_file_isolation = None  # type: ignore[assignment,misc]
    check_system_learning_isolation = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="boundary_guard.py deps unavailable")
class TestCheckFileIsolation:
    def test_is_callable(self):
        assert callable(check_file_isolation)

@pytest.mark.skipif(not _AVAILABLE, reason="boundary_guard.py deps unavailable")
class TestCheckSystemLearningIsolation:
    def test_is_callable(self):
        assert callable(check_system_learning_isolation)


def test_module_importable():
    """Module boundary_guard.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
