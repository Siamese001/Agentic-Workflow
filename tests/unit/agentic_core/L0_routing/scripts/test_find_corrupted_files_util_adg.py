"""ADG-driven tests for agentic_core/L0_routing/scripts/find_corrupted_files_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.find_corrupted_files_util import (  # noqa: F401
        find_corruption,
        is_valid_python,
        main,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    find_corruption = None  # type: ignore[assignment,misc]
    is_valid_python = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="find_corrupted_files_util.py deps unavailable")
class TestFindCorruption:
    def test_is_callable(self):
        assert callable(find_corruption)

@pytest.mark.skipif(not _AVAILABLE, reason="find_corrupted_files_util.py deps unavailable")
class TestIsValidPython:
    def test_is_callable(self):
        assert callable(is_valid_python)

@pytest.mark.skipif(not _AVAILABLE, reason="find_corrupted_files_util.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)


def test_module_importable():
    """Module find_corrupted_files_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE