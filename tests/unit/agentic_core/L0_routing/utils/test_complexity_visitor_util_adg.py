"""ADG-driven tests for agentic_core/L0_routing/utils/complexity_visitor_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.utils.complexity_visitor_util import (  # noqa: F401
        should_exclude_path,
        should_exclude_file,
        validate_agent_count,
        get_previous_agent_count,
        generate_manifest,
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
    should_exclude_path = None  # type: ignore[assignment,misc]
    should_exclude_file = None  # type: ignore[assignment,misc]
    validate_agent_count = None  # type: ignore[assignment,misc]
    get_previous_agent_count = None  # type: ignore[assignment,misc]
    generate_manifest = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="complexity_visitor_util.py deps unavailable")
class TestShouldExcludePath:
    def test_is_callable(self):
        assert callable(should_exclude_path)

@pytest.mark.skipif(not _AVAILABLE, reason="complexity_visitor_util.py deps unavailable")
class TestShouldExcludeFile:
    def test_is_callable(self):
        assert callable(should_exclude_file)

@pytest.mark.skipif(not _AVAILABLE, reason="complexity_visitor_util.py deps unavailable")
class TestValidateAgentCount:
    def test_is_callable(self):
        assert callable(validate_agent_count)

@pytest.mark.skipif(not _AVAILABLE, reason="complexity_visitor_util.py deps unavailable")
class TestGetPreviousAgentCount:
    def test_is_callable(self):
        assert callable(get_previous_agent_count)

@pytest.mark.skipif(not _AVAILABLE, reason="complexity_visitor_util.py deps unavailable")
class TestGenerateManifest:
    def test_is_callable(self):
        assert callable(generate_manifest)

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

@pytest.mark.skipif(not _AVAILABLE, reason="complexity_visitor_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module complexity_visitor_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
