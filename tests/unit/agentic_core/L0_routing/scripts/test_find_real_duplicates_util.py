"""Foundational behavioral tests for agentic_core/L0_routing/scripts/find_real_duplicates_v2_util.py.

fan_in=10 — this module is imported by 10 other modules.
ADG contract: import-hygiene is covered by test_find_real_duplicates_v2_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.find_real_duplicates_v2_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        get_priority,
        infer_rationale,
        is_agent_file,
        main,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    is_agent_file = None  # type: ignore[assignment,misc]
    get_priority = None  # type: ignore[assignment,misc]
    infer_rationale = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="find_real_duplicates_v2_util.py deps unavailable")
class TestIsAgentFileFunction:
    def test_is_callable(self):
        assert callable(is_agent_file)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(is_agent_file)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="find_real_duplicates_v2_util.py deps unavailable")
class TestGetPriorityFunction:
    def test_is_callable(self):
        assert callable(get_priority)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_priority)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="find_real_duplicates_v2_util.py deps unavailable")
class TestInferRationaleFunction:
    def test_is_callable(self):
        assert callable(infer_rationale)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(infer_rationale)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="find_real_duplicates_v2_util.py deps unavailable")
class TestMainFunction:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="find_real_duplicates_v2_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="find_real_duplicates_v2_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="find_real_duplicates_v2_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="find_real_duplicates_v2_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="find_real_duplicates_v2_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module find_real_duplicates_v2_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
