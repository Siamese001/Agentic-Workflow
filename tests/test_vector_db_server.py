"""Tests for the thin MCP adapter + retrieval service split."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

chromadb = pytest.importorskip("chromadb")
import numpy as np

from tools.mcp.vector_db_server import VectorDBMCPServer
from tools.retrieval.embedder import EmbeddingRuntime
from tools.retrieval.vector_service import VectorRetrievalService
from tools.retrieval.vector_store import ChromaVectorStore


def _make_service(
    ephemeral_client: chromadb.EphemeralClient,
    model: object | None = None,
) -> VectorRetrievalService:
    store = ChromaVectorStore(client_override=ephemeral_client)
    embedder = EmbeddingRuntime(model_override=model)
    return VectorRetrievalService(store=store, embedder=embedder)


@pytest.fixture()
def ephemeral() -> chromadb.EphemeralClient:
    return chromadb.EphemeralClient()


@pytest.fixture()
def mock_model():
    model = MagicMock()
    model.encode.side_effect = lambda texts, **kw: np.array([[0.1] * 1024] * len(texts), dtype=np.float32)
    model.get_sentence_embedding_dimension.return_value = 1024
    return model


@pytest.fixture()
def service(ephemeral, mock_model) -> VectorRetrievalService:
    return _make_service(ephemeral, mock_model)


@pytest.fixture()
def server(service: VectorRetrievalService) -> VectorDBMCPServer:
    return VectorDBMCPServer(service=service)


def test_service_create_collection_success(service, ephemeral):
    report = service.create_collection("test_col")
    assert "created successfully" in report.message
    assert ephemeral.get_collection("test_col") is not None


def test_service_create_collection_duplicate_raises(service, ephemeral):
    ephemeral.create_collection("dupe_col")
    with pytest.raises(Exception, match="already exists"):
        service.create_collection("dupe_col")


@pytest.mark.asyncio
async def test_adapter_returns_error_envelope_for_duplicate(server, ephemeral):
    ephemeral.create_collection("dupe")
    result = await server._create_collection({"name": "dupe"})
    assert result.isError is True
    assert "already exists" in result.content[0].text


def test_service_add_documents_auto_ids_are_unique(service, ephemeral):
    ephemeral.create_collection("id_test")
    report1 = service.add_documents("id_test", ["doc a", "doc b"])
    report2 = service.add_documents("id_test", ["doc c", "doc d"])
    assert "Added 2 documents" in report1.message
    assert "Added 2 documents" in report2.message

    collection = ephemeral.get_collection("id_test")
    stored = collection.get(include=[])
    ids = stored["ids"]
    assert len(ids) == 4
    assert len(set(ids)) == 4


def test_service_query_collection_empty_query_rejected(service, ephemeral):
    ephemeral.create_collection("q_test")
    with pytest.raises(Exception, match="EMPTY_QUERY"):
        service.query_collection("q_test", "   ")


@pytest.mark.asyncio
async def test_adapter_query_collection_formats_results(server, ephemeral, mock_model):
    ephemeral.create_collection("q_fmt")
    collection = ephemeral.get_collection("q_fmt")
    collection.upsert(
        ids=["a1"],
        documents=["hello world"],
        embeddings=[[0.1] * 1024],
        metadatas=[{"source": "unit"}],
    )

    result = await server._query_collection({"collection_name": "q_fmt", "query_text": "hello"})
    assert result.isError is False
    text = result.content[0].text
    assert "Query Results for 'q_fmt'" in text
    assert "hello world" in text


def test_service_embed_text_return_vectors_flag(service, mock_model):
    vec = [round(0.1 * i, 4) for i in range(1024)]
    mock_model.encode.side_effect = None  # clear fixture side_effect so return_value is active
    mock_model.encode.return_value = np.array([vec], dtype=np.float32)
    report = service.embed_text(["hello"], return_vectors=True)
    assert report.return_vectors is True
    assert report.previews[0].full_vector is not None
    assert len(report.previews[0].full_vector) == 1024
    assert abs(report.previews[0].full_vector[0]) < 1e-6
    assert abs(report.previews[0].full_vector[1] - 0.1) < 1e-3
    formatted = service.format_embed_text(["hello"], return_vectors=True)
    assert "Full vectors" in formatted
    assert "return_vectors: True" in formatted


def test_service_embed_text_zero_duration_safe(service, mock_model, monkeypatch):
    mock_model.encode.return_value = np.array([[0.1] * 1024], dtype=np.float32)

    class _FakeTime:
        values = [0.0, 0.0]

        @classmethod
        def time(cls):
            return cls.values.pop(0)

    monkeypatch.setattr("tools.retrieval.vector_service.time", _FakeTime)
    report = service.embed_text(["hello"])
    assert report.texts_per_second > 0


def test_service_semantic_search_sorted_by_distance(service, ephemeral, mock_model):
    for name in ("a_col", "b_col"):
        ephemeral.create_collection(name)

    controlled = {
        "a_col": {"documents": [["doc_far"]], "distances": [[0.9]], "metadatas": [[{}]]},
        "b_col": {"documents": [["doc_near"]], "distances": [[0.1]], "metadatas": [[{}]]},
    }
    original_get = ephemeral.get_collection

    def patched_get(name: str):
        col = original_get(name)
        mock_col = MagicMock(wraps=col)
        mock_col.query.return_value = controlled[name]
        return mock_col

    service.chroma_client = MagicMock()
    service.chroma_client.list_collections.return_value = []
    service.chroma_client.get_collection.side_effect = patched_get

    report = service.semantic_search("test", collections=["a_col", "b_col"], n_results=5)
    assert report.hits[0].document == "doc_near"
    assert report.hits[1].document == "doc_far"

    text = service.format_semantic_search("test", collections=["a_col", "b_col"], n_results=5)
    assert text.index("doc_near") < text.index("doc_far")


def test_service_semantic_search_tie_break_is_deterministic(service):
    service.chroma_client = MagicMock()
    service.chroma_client.list_collections.return_value = []

    alpha_col = MagicMock()
    alpha_col.query.return_value = {"documents": [["alpha"]], "distances": [[0.5]], "metadatas": [[{}]]}
    beta_col = MagicMock()
    beta_col.query.return_value = {"documents": [["beta"]], "distances": [[0.5]], "metadatas": [[{}]]}

    service.chroma_client.get_collection.side_effect = lambda name: {
        "tie_a": alpha_col,
        "tie_b": beta_col,
    }[name]

    first = service.format_semantic_search("test", collections=["tie_a", "tie_b"], n_results=5)
    second = service.format_semantic_search("test", collections=["tie_a", "tie_b"], n_results=5)
    assert first == second
    assert first.index("alpha") < first.index("beta")


def test_vector_stats_reports_directory_bytes(service, tmp_path, monkeypatch):
    fake_chroma = tmp_path / "chroma"
    fake_chroma.mkdir()
    (fake_chroma / "file_a.bin").write_bytes(b"x" * 1000)
    (fake_chroma / "file_b.bin").write_bytes(b"x" * 2000)

    monkeypatch.setattr("tools.retrieval.vector_store.CHROMA_PATH", fake_chroma)
    monkeypatch.setattr(service.store, "chroma_path", fake_chroma)

    stats = service.vector_stats()
    assert stats.disk_bytes == 3000
    text = service.format_vector_stats()
    assert "Disk bytes: 3000" in text


def test_list_collections_remains_hot_path_and_placeholder_count(service, ephemeral):
    ephemeral.create_collection("col1")
    text = service.format_list_collections()
    assert "Count: use get_collection_info or vector_stats" in text


@pytest.mark.asyncio
async def test_adapter_proxies_overrides(server, ephemeral, mock_model):
    new_client = chromadb.EphemeralClient()
    new_model = MagicMock()
    new_model.encode.return_value = np.array([[0.2] * 1024], dtype=np.float32)

    server.chroma_client = new_client
    server.embedding_model = new_model

    assert server.chroma_client is new_client
    assert server.embedding_model is new_model


# ---------------------------------------------------------------------------
# G1: EmbeddingRuntime device / fp16 wiring
# ---------------------------------------------------------------------------


def test_embedding_runtime_stores_device():
    """EmbeddingRuntime must persist the device kwarg as self.device."""
    rt = EmbeddingRuntime(device="cuda")
    assert rt.device == "cuda"


def test_apply_fp16_calls_half_on_cuda():
    """_apply_fp16_if_cuda must call model.half() when device='cuda'."""
    rt = EmbeddingRuntime(device="cuda")
    mock = MagicMock()
    rt._apply_fp16_if_cuda(mock)
    mock.half.assert_called_once()


def test_apply_fp16_skips_half_on_cpu():
    """_apply_fp16_if_cuda must NOT call model.half() when device='cpu'."""
    rt = EmbeddingRuntime(device="cpu")
    mock = MagicMock()
    rt._apply_fp16_if_cuda(mock)
    mock.half.assert_not_called()


# ---------------------------------------------------------------------------
# G4: cache_entry_types BGE-M3 constants
# ---------------------------------------------------------------------------


def test_cache_entry_types_embedding_constants_are_bgem3():
    """EMBEDDING_MODEL and EMBEDDING_DIM must be 'BAAI/bge-m3' and 1024 after BGE-M3 phase."""
    from agentic_core.runtime.types.cache_entry_types import EMBEDDING_DIM, EMBEDDING_MODEL

    assert EMBEDDING_MODEL == "BAAI/bge-m3"
    assert EMBEDDING_DIM == 1024


# ---------------------------------------------------------------------------
# G5: SemanticMemory BGE-M3 stub dimensions
# ---------------------------------------------------------------------------


def test_semantic_memory_bgem3_dimensions():
    """EmbeddingProvider.embed() must return 1024-dim; VectorIndex must default to dimension=1024."""
    from agentic_core.L1_cognition.reasoning.SemanticMemory import EmbeddingProvider, VectorIndex

    ep = EmbeddingProvider()
    assert len(ep.embed("any text")) == 1024
    vi = VectorIndex()
    assert vi.dimension == 1024
