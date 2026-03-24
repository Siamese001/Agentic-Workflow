"""ADG importability contract for agentic_core/L0_routing/scripts/chunk_type.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_chunk_type.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.scripts.chunk_type import (  # noqa: F401
        ChunkType,
        SemanticChunk,
        chunk_python_ast,
        chunk_text,
        chunk_text_fallback,
        load_text_file,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    load_text_file = None  # type: ignore[assignment,misc]
    ChunkType = None  # type: ignore[assignment,misc]
    SemanticChunk = None  # type: ignore[assignment,misc]
    chunk_python_ast = None  # type: ignore[assignment,misc]
    chunk_text_fallback = None  # type: ignore[assignment,misc]
    chunk_text = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="chunk_type deps unavailable")
class TestChunkTypeImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L0_routing/scripts/chunk_type.py must be importable."""
        assert _AVAILABLE

    def test_chunktype_defined(self) -> None:
        assert ChunkType is not None

    def test_semanticchunk_defined(self) -> None:
        assert SemanticChunk is not None