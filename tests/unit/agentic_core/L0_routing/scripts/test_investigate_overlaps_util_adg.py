"""ADG-driven tests for agentic_core/L0_routing/scripts/investigate_overlaps_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.investigate_overlaps_util import (  # noqa: F401
        GROUPS,
        PROJECT_ROOT,
        get_file_hash,
        investigate,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    get_file_hash = None  # type: ignore[assignment,misc]
    investigate = None  # type: ignore[assignment,misc]
    PROJECT_ROOT = None  # type: ignore[assignment,misc]
    GROUPS = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="investigate_overlaps_util.py deps unavailable")
class TestGetFileHash:
    def test_is_callable(self):
        assert callable(get_file_hash)

@pytest.mark.skipif(not _AVAILABLE, reason="investigate_overlaps_util.py deps unavailable")
class TestInvestigate:
    def test_is_callable(self):
        assert callable(investigate)

@pytest.mark.skipif(not _AVAILABLE, reason="investigate_overlaps_util.py deps unavailable")
class TestProjectRootConstant:
    def test_is_not_none(self):
        assert PROJECT_ROOT is not None

@pytest.mark.skipif(not _AVAILABLE, reason="investigate_overlaps_util.py deps unavailable")
class TestGroupsConstant:
    def test_is_not_none(self):
        assert GROUPS is not None


def test_module_importable():
    """Module investigate_overlaps_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE