"""Tests for the ADR-063 chunker catalog seed."""

from __future__ import annotations

import json

from tools.ingestion.chunker_catalog import (
    AstThinChunker,
    CausalWindowChunker,
    MarkdownHeaderChunker,
    PlainTextChunker,
    chunk_text,
    resolve,
)


def test_catalog_resolves_markdown_and_falls_back_for_unknown_source_kind():
    assert isinstance(resolve("docs/markdown"), MarkdownHeaderChunker)
    assert isinstance(resolve("unknown/source"), PlainTextChunker)


def test_markdown_header_chunker_stamps_capped_lineage():
    text = "\n".join(
        [
            "# ADR-063",
            "intro",
            "## Decision",
            "body",
            "### Normative Requirements",
            "req",
            "#### Catalog",
            "details",
            "##### Too Deep",
            "still capped",
        ]
    )

    chunks = chunk_text("docs/markdown", text, source_path="docs/architecture/adr/ADR-063.md")

    assert chunks
    deepest = chunks[-1]
    assert deepest.metadata["chunker_name"] == "markdown_header/v1"
    assert deepest.metadata["header_lineage"] == [
        "ADR-063",
        "Decision",
        "Normative Requirements",
        "Too Deep",
    ]
    assert len(deepest.metadata["header_lineage"]) == 4


def test_ast_thin_chunker_recovers_zero_arg_function_and_constant():
    source = "\n".join(
        [
            "MAX_RETRIES = 3",
            "",
            "def heartbeat():",
            "    pass",
            "",
            "class EmptyPolicy:",
            "    \"\"\"Marker policy.\"\"\"",
            "    pass",
        ]
    )

    chunks = AstThinChunker().chunk(source, source_kind="code/python", source_path="pkg/policy.py")
    names = {chunk.metadata["symbol_name"]: chunk for chunk in chunks}

    assert {"MAX_RETRIES", "heartbeat", "EmptyPolicy"} <= set(names)
    assert names["heartbeat"].metadata["chunk_kind"] == "thin"
    assert names["EmptyPolicy"].metadata["chunk_kind"] == "thin"


def test_causal_window_chunker_groups_rows_by_trace_id():
    text = "\n".join(
        [
            json.dumps({"trace_id": "t1", "span_id": "s1", "agent_class": "retrieval"}),
            json.dumps({"trace_id": "t1", "span_id": "s2", "agent_class": "retrieval"}),
            json.dumps({"trace_id": "t2", "span_id": "s3", "agent_class": "planner"}),
        ]
    )

    chunks = CausalWindowChunker().chunk(text, source_kind="traces/jsonl", source_path="trace.jsonl")

    assert [chunk.metadata["trace_id"] for chunk in chunks] == ["t1", "t2"]
    assert chunks[0].metadata["span_count"] == 2
