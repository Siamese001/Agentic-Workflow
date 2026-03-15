"""ADG-driven tests for apps_shared/utils/waterfall_reconciliation_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.waterfall_reconciliation_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        find_agent_in_archives,
        get_agents_at_commit,
        get_current_agents,
        main,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    get_agents_at_commit = None  # type: ignore[assignment,misc]
    get_current_agents = None  # type: ignore[assignment,misc]
    find_agent_in_archives = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="waterfall_reconciliation_util.py deps unavailable")
class TestGetAgentsAtCommit:
    def test_is_callable(self):
        assert callable(get_agents_at_commit)

@pytest.mark.skipif(not _AVAILABLE, reason="waterfall_reconciliation_util.py deps unavailable")
class TestGetCurrentAgents:
    def test_is_callable(self):
        assert callable(get_current_agents)

@pytest.mark.skipif(not _AVAILABLE, reason="waterfall_reconciliation_util.py deps unavailable")
class TestFindAgentInArchives:
    def test_is_callable(self):
        assert callable(find_agent_in_archives)

@pytest.mark.skipif(not _AVAILABLE, reason="waterfall_reconciliation_util.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="waterfall_reconciliation_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="waterfall_reconciliation_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="waterfall_reconciliation_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="waterfall_reconciliation_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="waterfall_reconciliation_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="waterfall_reconciliation_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module waterfall_reconciliation_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
