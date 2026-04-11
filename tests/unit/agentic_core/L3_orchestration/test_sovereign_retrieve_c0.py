"""Tests for C0EvidenceContract production in SovereignRagOrchestrator.sovereign_retrieve().

Verifies:
- Result dict contains "c0_contract" key after retrieval.
- CitedSpan fields are correctly mapped from AnchoredResult anchor attributes.
- Empty final_docs produces an abstain contract (abstain_hint=True).
- Original result shape (documents, anchors, faithfulness, etc.) is preserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

pytestmark = pytest.mark.asyncio

import agentic_core.L3_orchestration.reasoning.engines.sovereign_rag_orchestrator as _sro_module
from agentic_core.L3_orchestration.reasoning.engines.sovereign_rag_orchestrator import (
    SovereignRagOrchestrator,
)
from agentic_core.L3_orchestration.types.c0_evidence_contract_types import C0EvidenceContract


def _make_mock_config() -> MagicMock:
    cfg = MagicMock()
    cfg.budget.max_k = 5
    cfg.routing.depth_breaker = 1
    return cfg


def _make_mock_doc(
    content: str = "retrieved content about the system",
    doc_id: str = "doc-001",
    chunk_id: str = "chunk-001",
    content_hash: str = "abcdef1234567890",
    score: float = 0.9,
) -> MagicMock:
    doc = MagicMock()
    doc.content = content
    doc.doc_id = doc_id
    doc.chunk_id = chunk_id
    doc.content_hash = content_hash
    doc.score = score
    return doc


def _make_orchestrator(
    monkeypatch,
    mock_doc: MagicMock | None = None,
    empty: bool = False,
) -> tuple[SovereignRagOrchestrator, AsyncMock, AsyncMock, AsyncMock]:
    mock_cfg = _make_mock_config()
    monkeypatch.setattr(_sro_module, "get_active_configs", MagicMock(return_value=mock_cfg), raising=False)

    docs = [] if empty else [mock_doc or _make_mock_doc()]

    mock_planner = AsyncMock()
    mock_planner.decompose_query.return_value = ["test query"]
    mock_planner.multi_query_generation.return_value = ["test query"]

    mock_retriever = AsyncMock()
    mock_retriever.hybrid_search.return_value = docs
    mock_retriever.deduplicate_by_hash = MagicMock(return_value=docs)

    mock_guardrail = AsyncMock()
    mock_guardrail.rerank_documents.return_value = docs

    orchestrator = SovereignRagOrchestrator(
        retriever=mock_retriever,
        query_planner=mock_planner,
        guardrail=mock_guardrail,
    )
    return orchestrator, mock_planner, mock_retriever, mock_guardrail


async def test_sovereign_retrieve_result_contains_c0_contract_key(monkeypatch):
    orchestrator, _, _, _ = _make_orchestrator(monkeypatch)
    result = await orchestrator.sovereign_retrieve("test query", top_k=1)
    assert "c0_contract" in result


async def test_sovereign_retrieve_contract_is_c0_evidence_contract(monkeypatch):
    orchestrator, _, _, _ = _make_orchestrator(monkeypatch)
    result = await orchestrator.sovereign_retrieve("test query", top_k=1)
    assert isinstance(result["c0_contract"], C0EvidenceContract)


async def test_sovereign_retrieve_cited_span_source_ref_mapped_from_doc_id(monkeypatch):
    doc = _make_mock_doc(doc_id="my-doc-42")
    orchestrator, _, _, _ = _make_orchestrator(monkeypatch, mock_doc=doc)
    result = await orchestrator.sovereign_retrieve("test query", top_k=1)
    contract: C0EvidenceContract = result["c0_contract"]
    assert len(contract.cited_spans) == 1
    assert contract.cited_spans[0].source_ref == "my-doc-42"


async def test_sovereign_retrieve_cited_span_span_id_mapped_from_chunk_id(monkeypatch):
    doc = _make_mock_doc(chunk_id="chunk-xyz-99")
    orchestrator, _, _, _ = _make_orchestrator(monkeypatch, mock_doc=doc)
    result = await orchestrator.sovereign_retrieve("test query", top_k=1)
    assert result["c0_contract"].cited_spans[0].span_id == "chunk-xyz-99"


async def test_sovereign_retrieve_cited_span_chunk_hash_mapped_from_content_hash(monkeypatch):
    doc = _make_mock_doc(content_hash="deadbeef00112233")
    orchestrator, _, _, _ = _make_orchestrator(monkeypatch, mock_doc=doc)
    result = await orchestrator.sovereign_retrieve("test query", top_k=1)
    assert result["c0_contract"].cited_spans[0].chunk_hash == "deadbeef00112233"


async def test_sovereign_retrieve_cited_span_text_snippet_truncated_to_200(monkeypatch):
    long_content = "x" * 300
    doc = _make_mock_doc(content=long_content)
    orchestrator, _, _, _ = _make_orchestrator(monkeypatch, mock_doc=doc)
    result = await orchestrator.sovereign_retrieve("test query", top_k=1)
    assert result["c0_contract"].cited_spans[0].text_snippet == "x" * 200


async def test_sovereign_retrieve_cited_span_relevance_score_from_doc_score(monkeypatch):
    doc = _make_mock_doc(score=0.77)
    orchestrator, _, _, _ = _make_orchestrator(monkeypatch, mock_doc=doc)
    result = await orchestrator.sovereign_retrieve("test query", top_k=1)
    assert result["c0_contract"].cited_spans[0].relevance_score == pytest.approx(0.77)


async def test_sovereign_retrieve_empty_docs_produces_abstain_contract(monkeypatch):
    orchestrator, _, _, _ = _make_orchestrator(monkeypatch, empty=True)
    result = await orchestrator.sovereign_retrieve("empty query", top_k=1)
    contract: C0EvidenceContract = result["c0_contract"]
    assert contract is not None
    assert contract.abstain_hint is True
    assert len(contract.cited_spans) == 0


async def test_sovereign_retrieve_preserves_original_result_shape(monkeypatch):
    orchestrator, _, _, _ = _make_orchestrator(monkeypatch)
    result = await orchestrator.sovereign_retrieve("test query", top_k=1)
    for key in ("query", "documents", "anchors", "faithfulness", "top_k", "hops"):
        assert key in result, f"Missing key: {key}"
    assert result["faithfulness"] == pytest.approx(0.85)
    assert result["query"] == "test query"
