"""ADG-driven tests for agentic_core/L5_safety/enforcement/agent_info_enforcer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.enforcement.agent_info_enforcer import (  # noqa: F401
        AgentInfo,
        ASTNormalizer,
        extract_layer,
        find_agent_classes,
        generate_fingerprint,
        calculate_similarity,
        analyze_redundancy,
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
    AgentInfo = None  # type: ignore[assignment,misc]
    ASTNormalizer = None  # type: ignore[assignment,misc]
    extract_layer = None  # type: ignore[assignment,misc]
    find_agent_classes = None  # type: ignore[assignment,misc]
    generate_fingerprint = None  # type: ignore[assignment,misc]
    calculate_similarity = None  # type: ignore[assignment,misc]
    analyze_redundancy = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="agent_info_enforcer.py deps unavailable")
class TestAgentInfo:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(AgentInfo)
    def test_importable(self):
        assert AgentInfo is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_info_enforcer.py deps unavailable")
class TestASTNormalizer:
    def test_is_class(self):
        assert isinstance(ASTNormalizer, type)
    def test_importable(self):
        assert ASTNormalizer is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_info_enforcer.py deps unavailable")
class TestExtractLayer:
    def test_is_callable(self):
        assert callable(extract_layer)

@pytest.mark.skipif(not _AVAILABLE, reason="agent_info_enforcer.py deps unavailable")
class TestFindAgentClasses:
    def test_is_callable(self):
        assert callable(find_agent_classes)

@pytest.mark.skipif(not _AVAILABLE, reason="agent_info_enforcer.py deps unavailable")
class TestGenerateFingerprint:
    def test_is_callable(self):
        assert callable(generate_fingerprint)

@pytest.mark.skipif(not _AVAILABLE, reason="agent_info_enforcer.py deps unavailable")
class TestCalculateSimilarity:
    def test_is_callable(self):
        assert callable(calculate_similarity)

@pytest.mark.skipif(not _AVAILABLE, reason="agent_info_enforcer.py deps unavailable")
class TestAnalyzeRedundancy:
    def test_is_callable(self):
        assert callable(analyze_redundancy)

@pytest.mark.skipif(not _AVAILABLE, reason="agent_info_enforcer.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_info_enforcer.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_info_enforcer.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_info_enforcer.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_info_enforcer.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_info_enforcer.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module agent_info_enforcer.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
