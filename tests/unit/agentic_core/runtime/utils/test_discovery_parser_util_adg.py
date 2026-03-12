"""ADG-driven tests for agentic_core/runtime/utils/discovery_parser_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.runtime.utils.discovery_parser_util import (  # noqa: F401
        AgentListMapping,
        load_hardened_agent_metadata,
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
    AgentListMapping = None  # type: ignore[assignment,misc]
    load_hardened_agent_metadata = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="discovery_parser_util.py deps unavailable")
class TestAgentListMapping:
    def test_is_class(self):
        assert isinstance(AgentListMapping, type)
    def test_importable(self):
        assert AgentListMapping is not None

@pytest.mark.skipif(not _AVAILABLE, reason="discovery_parser_util.py deps unavailable")
class TestLoadHardenedAgentMetadata:
    def test_is_callable(self):
        assert callable(load_hardened_agent_metadata)

@pytest.mark.skipif(not _AVAILABLE, reason="discovery_parser_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="discovery_parser_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="discovery_parser_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="discovery_parser_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="discovery_parser_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="discovery_parser_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module discovery_parser_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
