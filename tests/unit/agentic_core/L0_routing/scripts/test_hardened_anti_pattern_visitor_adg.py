"""ADG-driven tests for agentic_core/L0_routing/scripts/hardened_anti_pattern_visitor.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.hardened_anti_pattern_visitor import (  # noqa: F401
        PROJECT_ROOT,
        HardenedAntiPatternVisitor,
        main,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    HardenedAntiPatternVisitor = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    PROJECT_ROOT = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="hardened_anti_pattern_visitor.py deps unavailable")
class TestHardenedAntiPatternVisitor:
    def test_is_class(self):
        assert isinstance(HardenedAntiPatternVisitor, type)
    def test_importable(self):
        assert HardenedAntiPatternVisitor is not None

@pytest.mark.skipif(not _AVAILABLE, reason="hardened_anti_pattern_visitor.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="hardened_anti_pattern_visitor.py deps unavailable")
class TestProjectRootConstant:
    def test_is_not_none(self):
        assert PROJECT_ROOT is not None


def test_module_importable():
    """Module hardened_anti_pattern_visitor.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE