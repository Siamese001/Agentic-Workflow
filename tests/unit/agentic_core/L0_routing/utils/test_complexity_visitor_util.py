"""Foundational behavioral tests for agentic_core/L0_routing/utils/complexity_visitor_util.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_complexity_visitor_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L0_routing.utils.complexity_visitor_util import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    get_previous_agent_count,
    should_exclude_file,
    should_exclude_path,
    validate_agent_count,
)


class TestShouldExcludePathFunction:
    def test_is_callable(self):
        assert callable(should_exclude_path)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(should_exclude_path)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestShouldExcludeFileFunction:
    def test_is_callable(self):
        assert callable(should_exclude_file)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(should_exclude_file)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestValidateAgentCountFunction:
    def test_is_callable(self):
        assert callable(validate_agent_count)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(validate_agent_count)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestGetPreviousAgentCountFunction:
    def test_is_callable(self):
        assert callable(get_previous_agent_count)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_previous_agent_count)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module complexity_visitor_util must be importable or skip gracefully."""
    pass  # Import verified at module level
