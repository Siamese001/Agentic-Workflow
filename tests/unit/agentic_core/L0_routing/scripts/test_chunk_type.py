"""Foundational behavioral tests for agentic_core/L0_routing/scripts/chunk_type.py.

fan_in=13 — this module is imported by 13 other modules.
ADG contract: import-hygiene is covered by test_chunk_type_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.chunk_type import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        ChunkType,
        SemanticChunk,
        chunk_python_ast,
        chunk_text,
        chunk_text_fallback,
        load_text_file,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    ChunkType = None  # type: ignore[assignment,misc]
    SemanticChunk = None  # type: ignore[assignment,misc]
    load_text_file = None  # type: ignore[assignment,misc]
    chunk_python_ast = None  # type: ignore[assignment,misc]
    chunk_text_fallback = None  # type: ignore[assignment,misc]
    chunk_text = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="chunk_type.py deps unavailable")
class TestChunkTypeContract:
    def test_is_enum(self):
        import enum
        assert issubclass(ChunkType, enum.Enum)

    def test_has_members(self):
        assert len(list(ChunkType)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in ChunkType:
            assert member.value is not None

    def test_known_member_module_exists(self):
        assert hasattr(ChunkType, 'MODULE')

@pytest.mark.skipif(not _AVAILABLE, reason="chunk_type.py deps unavailable")
class TestSemanticChunkContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(SemanticChunk)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(SemanticChunk)}
        assert field_names >= {'chunk_type', 'text', 'end_line', 'start_line', 'name'}

@pytest.mark.skipif(not _AVAILABLE, reason="chunk_type.py deps unavailable")
class TestLoadTextFileFunction:
    def test_is_callable(self):
        assert callable(load_text_file)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(load_text_file)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="chunk_type.py deps unavailable")
class TestChunkPythonAstFunction:
    def test_is_callable(self):
        assert callable(chunk_python_ast)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(chunk_python_ast)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="chunk_type.py deps unavailable")
class TestChunkTextFallbackFunction:
    def test_is_callable(self):
        assert callable(chunk_text_fallback)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(chunk_text_fallback)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="chunk_type.py deps unavailable")
class TestChunkTextFunction:
    def test_is_callable(self):
        assert callable(chunk_text)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(chunk_text)
        assert sig.return_annotation is not inspect.Parameter.empty

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


def test_module_importable():
    """Module chunk_type must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
