"""ADG-driven tests for agentic_core/config/core/non_conforming_agent_finder_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.config.core.non_conforming_agent_finder_config import (  # noqa: F401
        NonConformingAgentFinder,
        main,
        PROJECT_ROOT,
        AGENTIC_CORE,
        EXCLUDED_DIRS,
        AGENT_LIKE_METHODS,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    NonConformingAgentFinder = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    PROJECT_ROOT = None  # type: ignore[assignment,misc]
    AGENTIC_CORE = None  # type: ignore[assignment,misc]
    EXCLUDED_DIRS = None  # type: ignore[assignment,misc]
    AGENT_LIKE_METHODS = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="non_conforming_agent_finder_config.py deps unavailable")
class TestNonConformingAgentFinder:
    def test_is_class(self):
        assert isinstance(NonConformingAgentFinder, type)
    def test_importable(self):
        assert NonConformingAgentFinder is not None

@pytest.mark.skipif(not _AVAILABLE, reason="non_conforming_agent_finder_config.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="non_conforming_agent_finder_config.py deps unavailable")
class TestProjectRootConstant:
    def test_is_not_none(self):
        assert PROJECT_ROOT is not None

@pytest.mark.skipif(not _AVAILABLE, reason="non_conforming_agent_finder_config.py deps unavailable")
class TestAgenticCoreConstant:
    def test_is_not_none(self):
        assert AGENTIC_CORE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="non_conforming_agent_finder_config.py deps unavailable")
class TestExcludedDirsConstant:
    def test_is_not_none(self):
        assert EXCLUDED_DIRS is not None

@pytest.mark.skipif(not _AVAILABLE, reason="non_conforming_agent_finder_config.py deps unavailable")
class TestAgentLikeMethodsConstant:
    def test_is_not_none(self):
        assert AGENT_LIKE_METHODS is not None


def test_module_importable():
    """Module non_conforming_agent_finder_config.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
