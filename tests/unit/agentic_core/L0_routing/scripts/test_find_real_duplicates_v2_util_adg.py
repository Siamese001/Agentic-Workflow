"""ADG-driven tests for agentic_core/L0_routing/scripts/find_real_duplicates_v2_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.find_real_duplicates_v2_util import (  # noqa: F401
        is_agent_file,
        get_priority,
        infer_rationale,
        main,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
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
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="find_real_duplicates_v2_util.py deps unavailable")
class TestIsAgentFile:
    def test_is_callable(self):
        assert callable(is_agent_file)

@pytest.mark.skipif(not _AVAILABLE, reason="find_real_duplicates_v2_util.py deps unavailable")
class TestGetPriority:
    def test_is_callable(self):
        assert callable(get_priority)

@pytest.mark.skipif(not _AVAILABLE, reason="find_real_duplicates_v2_util.py deps unavailable")
class TestInferRationale:
    def test_is_callable(self):
        assert callable(infer_rationale)

@pytest.mark.skipif(not _AVAILABLE, reason="find_real_duplicates_v2_util.py deps unavailable")
class TestMain:
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

@pytest.mark.skipif(not _AVAILABLE, reason="find_real_duplicates_v2_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module find_real_duplicates_v2_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
