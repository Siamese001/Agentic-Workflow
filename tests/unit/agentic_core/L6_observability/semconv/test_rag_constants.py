"""Tests for RAG OTel semconv constants — ADR-062 SSOT."""

from __future__ import annotations

import pytest

from agentic_core.L6_observability.semconv import rag


def test_all_span_names_unique() -> None:
    spans = (
        rag.SPAN_QUERY,
        rag.SPAN_QUERY_TRANSFORM,
        rag.SPAN_EMBED,
        rag.SPAN_SEARCH,
        rag.SPAN_FUSE,
        rag.SPAN_RERANK,
        rag.SPAN_GRADE,
        rag.SPAN_EXPAND,
    )
    assert len(spans) == len(set(spans))
    assert rag.ALL_SPAN_NAMES == frozenset(spans)


def test_span_names_share_namespace_prefix() -> None:
    for name in rag.ALL_SPAN_NAMES:
        assert name.startswith("gen_ai.retrieval."), f"{name!r} not under namespace"


@pytest.mark.parametrize(
    "attr_name,attr_value",
    [
        ("ATTR_RUN_ID", rag.ATTR_RUN_ID),
        ("ATTR_QUERY_HASH", rag.ATTR_QUERY_HASH),
        ("ATTR_TRANSFORM_NAME", rag.ATTR_TRANSFORM_NAME),
        ("ATTR_RERANKER_NAME", rag.ATTR_RERANKER_NAME),
        ("ATTR_LOOP_ITER", rag.ATTR_LOOP_ITER),
    ],
)
def test_attribute_keys_are_namespaced(attr_name: str, attr_value: str) -> None:
    assert attr_value.startswith("gen_ai."), f"{attr_name}={attr_value!r} not namespaced"


def test_outcome_set_complete() -> None:
    assert rag.VALID_OUTCOMES == frozenset({"converged", "cap", "budget_exceeded", "abstained", "error"})


def test_evidence_quality_set_complete() -> None:
    assert rag.VALID_EVIDENCE_QUALITIES == frozenset({"strong", "weak", "none"})


def test_dim_tier_set_complete() -> None:
    assert rag.VALID_DIM_TIERS == frozenset(
        {"hot-interactive", "warm-analytics", "cold-batch", "tiny-prefilter"}
    )


def test_embed_head_set_complete() -> None:
    assert rag.VALID_EMBED_HEADS == frozenset({"dense", "sparse", "colbert"})


def test_provenance_attrs_use_embedding_namespace() -> None:
    # ADR-055 attributes share a sibling namespace.
    assert rag.ATTR_PROVENANCE_MISMATCH == "gen_ai.embedding.provenance_mismatch"
    assert rag.ATTR_EXPECTED_MODEL == "gen_ai.embedding.expected_model"
    assert rag.ATTR_ACTUAL_MODEL == "gen_ai.embedding.actual_model"
