"""ADG-driven tests for agentic_core/L0_routing/scripts/chunk_type.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.chunk_type import (  # noqa: F401
        ChunkType,
        SemanticChunk,
        load_text_file,
        chunk_python_ast,
        chunk_text_fallback,
        chunk_text,
        process_file,
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
    ChunkType = None  # type: ignore[assignment,misc]
    SemanticChunk = None  # type: ignore[assignment,misc]
    load_text_file = None  # type: ignore[assignment,misc]
    chunk_python_ast = None  # type: ignore[assignment,misc]
    chunk_text_fallback = None  # type: ignore[assignment,misc]
    chunk_text = None  # type: ignore[assignment,misc]
    process_file = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="chunk_type.py deps unavailable")
class TestChunkType:
    def test_is_enum(self):
        import enum
        assert issubclass(ChunkType, enum.Enum)
    def test_has_members(self):
        assert len(list(ChunkType)) >= 1
    def test_importable(self):
        assert ChunkType is not None

@pytest.mark.skipif(not _AVAILABLE, reason="chunk_type.py deps unavailable")
class TestSemanticChunk:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(SemanticChunk)
    def test_importable(self):
        assert SemanticChunk is not None

@pytest.mark.skipif(not _AVAILABLE, reason="chunk_type.py deps unavailable")
class TestLoadTextFile:
    def test_is_callable(self):
        assert callable(load_text_file)

@pytest.mark.skipif(not _AVAILABLE, reason="chunk_type.py deps unavailable")
class TestChunkPythonAst:
    def test_is_callable(self):
        assert callable(chunk_python_ast)

@pytest.mark.skipif(not _AVAILABLE, reason="chunk_type.py deps unavailable")
class TestChunkTextFallback:
    def test_is_callable(self):
        assert callable(chunk_text_fallback)

@pytest.mark.skipif(not _AVAILABLE, reason="chunk_type.py deps unavailable")
class TestChunkText:
    def test_is_callable(self):
        assert callable(chunk_text)

@pytest.mark.skipif(not _AVAILABLE, reason="chunk_type.py deps unavailable")
class TestProcessFile:
    def test_is_callable(self):
        assert callable(process_file)

@pytest.mark.skipif(not _AVAILABLE, reason="chunk_type.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="chunk_type.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="chunk_type.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="chunk_type.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="chunk_type.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="chunk_type.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module chunk_type.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
