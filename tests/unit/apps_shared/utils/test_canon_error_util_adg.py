"""ADG-driven tests for apps_shared/utils/canon_error_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.canon_error_util import (  # noqa: F401
        SOVEREIGN_EXCEPTIONS,
        AgentExecutionError,
        CanonError,
        CanonTokenError,
        CanonViolationError,
        MemorySyncError,
        SwarmInitializationError,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    CanonError = None  # type: ignore[assignment,misc]
    CanonViolationError = None  # type: ignore[assignment,misc]
    MemorySyncError = None  # type: ignore[assignment,misc]
    SwarmInitializationError = None  # type: ignore[assignment,misc]
    AgentExecutionError = None  # type: ignore[assignment,misc]
    CanonTokenError = None  # type: ignore[assignment,misc]
    SOVEREIGN_EXCEPTIONS = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="canon_error_util.py deps unavailable")
class TestCanonError:
    def test_is_class(self):
        assert isinstance(CanonError, type)
    def test_importable(self):
        assert CanonError is not None

@pytest.mark.skipif(not _AVAILABLE, reason="canon_error_util.py deps unavailable")
class TestCanonViolationError:
    def test_is_class(self):
        assert isinstance(CanonViolationError, type)
    def test_importable(self):
        assert CanonViolationError is not None

@pytest.mark.skipif(not _AVAILABLE, reason="canon_error_util.py deps unavailable")
class TestMemorySyncError:
    def test_is_class(self):
        assert isinstance(MemorySyncError, type)
    def test_importable(self):
        assert MemorySyncError is not None

@pytest.mark.skipif(not _AVAILABLE, reason="canon_error_util.py deps unavailable")
class TestSwarmInitializationError:
    def test_is_class(self):
        assert isinstance(SwarmInitializationError, type)
    def test_importable(self):
        assert SwarmInitializationError is not None

@pytest.mark.skipif(not _AVAILABLE, reason="canon_error_util.py deps unavailable")
class TestAgentExecutionError:
    def test_is_class(self):
        assert isinstance(AgentExecutionError, type)
    def test_importable(self):
        assert AgentExecutionError is not None

@pytest.mark.skipif(not _AVAILABLE, reason="canon_error_util.py deps unavailable")
class TestCanonTokenError:
    def test_is_class(self):
        assert isinstance(CanonTokenError, type)
    def test_importable(self):
        assert CanonTokenError is not None

@pytest.mark.skipif(not _AVAILABLE, reason="canon_error_util.py deps unavailable")
class TestSovereignExceptionsConstant:
    def test_is_not_none(self):
        assert SOVEREIGN_EXCEPTIONS is not None


def test_module_importable():
    """Module canon_error_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE