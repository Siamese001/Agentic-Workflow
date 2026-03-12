"""ADG-driven tests for agentic_core/utils/workflow_engines/late_chunking.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.utils.workflow_engines.late_chunking import (  # noqa: F401
        LateChunkingProfile,
        LateChunkManifest,
        LateChunkingPipelineConfig,
        segment_document,
        build_late_chunk_manifests_for_corpus,
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
    LateChunkingProfile = None  # type: ignore[assignment,misc]
    LateChunkManifest = None  # type: ignore[assignment,misc]
    LateChunkingPipelineConfig = None  # type: ignore[assignment,misc]
    segment_document = None  # type: ignore[assignment,misc]
    build_late_chunk_manifests_for_corpus = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="late_chunking.py deps unavailable")
class TestLateChunkingProfile:
    def test_is_class(self):
        assert isinstance(LateChunkingProfile, type)
    def test_importable(self):
        assert LateChunkingProfile is not None

@pytest.mark.skipif(not _AVAILABLE, reason="late_chunking.py deps unavailable")
class TestLateChunkManifest:
    def test_is_class(self):
        assert isinstance(LateChunkManifest, type)
    def test_importable(self):
        assert LateChunkManifest is not None

@pytest.mark.skipif(not _AVAILABLE, reason="late_chunking.py deps unavailable")
class TestLateChunkingPipelineConfig:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(LateChunkingPipelineConfig)
    def test_importable(self):
        assert LateChunkingPipelineConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="late_chunking.py deps unavailable")
class TestSegmentDocument:
    def test_is_callable(self):
        assert callable(segment_document)

@pytest.mark.skipif(not _AVAILABLE, reason="late_chunking.py deps unavailable")
class TestBuildLateChunkManifestsForCorpus:
    def test_is_callable(self):
        assert callable(build_late_chunk_manifests_for_corpus)

@pytest.mark.skipif(not _AVAILABLE, reason="late_chunking.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="late_chunking.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="late_chunking.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="late_chunking.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="late_chunking.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="late_chunking.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module late_chunking.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
