"""Tests for the _apply_contextualization helper in tools.ingestion.ingest_code.

Guards the P1.1b wiring: chunks produced by the code ingestion pipeline get
enriched with Anthropic-style narrative context (heuristic fallback when no
gateway is injected) and the ``chunk_context`` metadata field is populated.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from tools.ingestion.contextual_chunk_builder import ContextualChunkBuilder
from tools.ingestion.ingest_code import CodeChunker, _apply_contextualization


def _chunk(file_path: str, content: str = "def foo(): pass", name: str = "foo") -> dict:
    return {
        "id": f"chunk-{name}",
        "content": content,
        "metadata": {
            "file_path": file_path,
            "module": "mod.submod",
            "name": name,
            "entity_type": "function",
            "layer": "L2",
            "line_start": 1,
            "line_end": 1,
            "type": "code",
        },
    }


def test_chunk_context_is_in_optional_metadata_fields():
    """Regression guard: the schema must allow chunk_context, otherwise
    validate_metadata will reject enriched chunks after contextualization."""
    assert "chunk_context" in CodeChunker.OPTIONAL_METADATA_FIELDS


def test_apply_contextualization_enriches_chunks_with_heuristic_fallback(tmp_path):
    # Write a real file the helper can read
    src_file = tmp_path / "example.py"
    src_file.write_text("def foo():\n    '''Demo function.'''\n    return 1\n", encoding="utf-8")
    logging.info("C3 write receipt: tests/_archived_obsolete/unit/tools/ingestion/test_ingest_code_contextualization.py write side effect recorded")

    chunks = [_chunk(file_path=str(src_file))]
    # No gateway -> heuristic path
    builder = ContextualChunkBuilder(enabled=False)
    enriched = _apply_contextualization(chunks, builder=builder)

    assert enriched == 1
    assert chunks[0]["metadata"].get("chunk_context")
    # Content should be prefixed with the context (heuristic uses module/name)
    assert (
        "foo" in chunks[0]["metadata"]["chunk_context"].lower()
        or "mod" in chunks[0]["metadata"]["chunk_context"].lower()
    )
    # The original chunk body must still appear after the prepended context
    assert "def foo(): pass" in chunks[0]["content"]


def test_apply_contextualization_reads_each_file_once(tmp_path):
    # Two chunks pointing at the same file — should read only once thanks to
    # the in-helper cache
    src_file = tmp_path / "shared.py"
    src_file.write_text("# shared module\n" * 50, encoding="utf-8")

    chunks = [
        _chunk(file_path=str(src_file), name="a"),
        _chunk(file_path=str(src_file), name="b"),
    ]
    read_count = {"n": 0}
    original_read = Path.read_text

    def counting_read(self, *args, **kwargs):
        read_count["n"] += 1
        return original_read(self, *args, **kwargs)

    import tools.ingestion.ingest_code as ingest_mod  # noqa: PLC0415

    # Monkeypatch only for this test: count reads of Path.read_text
    ingest_mod.Path = type("P", (Path,), {"read_text": counting_read})  # type: ignore[misc]
    try:
        builder = ContextualChunkBuilder(enabled=False)
        _apply_contextualization(chunks, builder=builder)
    finally:
        ingest_mod.Path = Path  # restore

    # Cache must deduplicate: at most one read regardless of chunk count
    assert read_count["n"] <= 1


def test_apply_contextualization_skips_chunk_without_file_path():
    chunks = [{"id": "c1", "content": "body", "metadata": {}}]
    builder = ContextualChunkBuilder(enabled=False)
    enriched = _apply_contextualization(chunks, builder=builder)
    assert enriched == 0
    # No chunk_context added since we couldn't ground it
    assert "chunk_context" not in chunks[0]["metadata"]


def test_apply_contextualization_tolerates_unreadable_file(tmp_path):
    # file_path points to a nonexistent file
    chunks = [_chunk(file_path=str(tmp_path / "missing.py"))]
    builder = ContextualChunkBuilder(enabled=False)
    enriched = _apply_contextualization(chunks, builder=builder)
    assert enriched == 0  # no crash; just skipped


def test_apply_contextualization_produces_valid_metadata(tmp_path):
    # After enrichment, validate_metadata must still pass — the OPTIONAL
    # field whitelist now includes chunk_context.
    src_file = tmp_path / "valid.py"
    src_file.write_text("def foo(): pass\n", encoding="utf-8")
    chunks = [_chunk(file_path=str(src_file))]
    _apply_contextualization(chunks, builder=ContextualChunkBuilder(enabled=False))

    is_valid, errors = CodeChunker.validate_metadata(chunks[0]["metadata"])
    assert is_valid, f"Metadata rejected after enrichment: {errors}"
