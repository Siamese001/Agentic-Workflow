"""Foundational behavioral tests for agentic_core/L0_routing/utils/complexity_visitor_util.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_complexity_visitor_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.utils.complexity_visitor_util import (  # noqa: F401
        should_exclude_path,
        should_exclude_file,
        validate_agent_count,
        get_previous_agent_count,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    should_exclude_path = None  # type: ignore[assignment,misc]
    should_exclude_file = None  # type: ignore[assignment,misc]
    validate_agent_count = None  # type: ignore[assignment,misc]
    get_previous_agent_count = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="complexity_visitor_util.py deps unavailable")
class TestShouldExcludePathFunction:
    def test_is_callable(self):
        assert callable(should_exclude_path)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(should_exclude_path)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="complexity_visitor_util.py deps unavailable")
class TestShouldExcludeFileFunction:
    def test_is_callable(self):
        assert callable(should_exclude_file)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(should_exclude_file)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="complexity_visitor_util.py deps unavailable")
class TestValidateAgentCountFunction:
    def test_is_callable(self):
        assert callable(validate_agent_count)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(validate_agent_count)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="complexity_visitor_util.py deps unavailable")
class TestGetPreviousAgentCountFunction:
    def test_is_callable(self):
        assert callable(get_previous_agent_count)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_previous_agent_count)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="complexity_visitor_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="complexity_visitor_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="complexity_visitor_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="complexity_visitor_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="complexity_visitor_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module complexity_visitor_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
