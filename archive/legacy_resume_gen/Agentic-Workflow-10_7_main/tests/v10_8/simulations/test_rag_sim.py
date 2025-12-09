"""Tests for RAG simulator."""

import pytest

from simulations.engines.rag_sim import RAGSimulator
from simulations.models import RAGSimRequest


@pytest.mark.asyncio
async def test_rag_simulator_returns_result():
    simulator = RAGSimulator()
    request = RAGSimRequest(
        simulation_id="sim-rag",
        payload={},
        query="test",
        documents=["doc1", "doc2", "doc3"],
    )
    result = await simulator.run(request)
    assert result.success is True
    assert 0.0 <= result.metrics["recall"] <= 1.0
    assert 0.0 <= result.metrics["precision"] <= 1.0
    assert 0.0 <= result.metrics["redundancy"] <= 1.0
    assert isinstance(result.details["top_documents"], list)


def test_rag_request_validation():
    request = RAGSimRequest(
        simulation_id="sim-rag-validate",
        payload={},
        query="hello",
        documents=["a"],
    )
    assert request.query == "hello"
    assert request.documents == ["a"]
