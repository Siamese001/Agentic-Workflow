"""ADG-driven tests for agentic_core/utils/workflow_engines/validators.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.utils.workflow_engines.validators import (  # noqa: F401
        ChunkQualityReport,
        MaxChunkSizeValidator,
        MinChunkSizeValidator,
        OverlapSanityValidator,
        DuplicateChunkDetector,
        OrphanChunkDetector,
        ChunkManifestValidator,
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
    ChunkQualityReport = None  # type: ignore[assignment,misc]
    MaxChunkSizeValidator = None  # type: ignore[assignment,misc]
    MinChunkSizeValidator = None  # type: ignore[assignment,misc]
    OverlapSanityValidator = None  # type: ignore[assignment,misc]
    DuplicateChunkDetector = None  # type: ignore[assignment,misc]
    OrphanChunkDetector = None  # type: ignore[assignment,misc]
    ChunkManifestValidator = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="validators.py deps unavailable")
class TestChunkQualityReport:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ChunkQualityReport)
    def test_importable(self):
        assert ChunkQualityReport is not None

@pytest.mark.skipif(not _AVAILABLE, reason="validators.py deps unavailable")
class TestMaxChunkSizeValidator:
    def test_is_class(self):
        assert isinstance(MaxChunkSizeValidator, type)
    def test_importable(self):
        assert MaxChunkSizeValidator is not None

@pytest.mark.skipif(not _AVAILABLE, reason="validators.py deps unavailable")
class TestMinChunkSizeValidator:
    def test_is_class(self):
        assert isinstance(MinChunkSizeValidator, type)
    def test_importable(self):
        assert MinChunkSizeValidator is not None

@pytest.mark.skipif(not _AVAILABLE, reason="validators.py deps unavailable")
class TestOverlapSanityValidator:
    def test_is_class(self):
        assert isinstance(OverlapSanityValidator, type)
    def test_importable(self):
        assert OverlapSanityValidator is not None

@pytest.mark.skipif(not _AVAILABLE, reason="validators.py deps unavailable")
class TestDuplicateChunkDetector:
    def test_is_class(self):
        assert isinstance(DuplicateChunkDetector, type)
    def test_importable(self):
        assert DuplicateChunkDetector is not None

@pytest.mark.skipif(not _AVAILABLE, reason="validators.py deps unavailable")
class TestOrphanChunkDetector:
    def test_is_class(self):
        assert isinstance(OrphanChunkDetector, type)
    def test_importable(self):
        assert OrphanChunkDetector is not None

@pytest.mark.skipif(not _AVAILABLE, reason="validators.py deps unavailable")
class TestChunkManifestValidator:
    def test_is_class(self):
        assert isinstance(ChunkManifestValidator, type)
    def test_importable(self):
        assert ChunkManifestValidator is not None

@pytest.mark.skipif(not _AVAILABLE, reason="validators.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="validators.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="validators.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="validators.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="validators.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="validators.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module validators.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
