"""Tests for apps_research.integrations.search_retrieval.apply_contextual_prefix (§P4.5)."""

from __future__ import annotations

from apps_research.integrations.search_retrieval import apply_contextual_prefix


def test_prefix_wraps_chunk_with_template():
    out = apply_contextual_prefix(
        "the chunk body",
        doc_title="Doc A",
        surrounding_text="Section overview",
    )
    assert "<document>Doc A</document>" in out
    assert "<chunk_context>Section overview</chunk_context>" in out
    assert out.endswith("the chunk body")


def test_prefix_empty_args_still_produces_template():
    out = apply_contextual_prefix("body")
    assert "<document></document>" in out
    assert "<chunk_context></chunk_context>" in out


def test_prefix_deterministic():
    a = apply_contextual_prefix("x", doc_title="d", surrounding_text="s")
    b = apply_contextual_prefix("x", doc_title="d", surrounding_text="s")
    assert a == b
