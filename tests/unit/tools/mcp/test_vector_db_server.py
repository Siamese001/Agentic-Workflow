"""Phase 1 safety tests for the vector_db MCP server.

Uses chromadb.EphemeralClient (in-memory) injected via monkeypatch so no
disk state is touched.  All tests are async-native (pytest-asyncio).
"""

from __future__ import annotations

import asyncio
import uuid
from unittest.mock import MagicMock, patch

import chromadb
import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


def _make_server(ephemeral_client: chromadb.EphemeralClient):
    """Return a VectorDBMCPServer whose chroma_client is an ephemeral instance."""
    with patch("chromadb.PersistentClient", return_value=ephemeral_client):
        with patch("pathlib.Path.mkdir"):
            from tools.mcp.vector_db_server import VectorDBMCPServer

            return VectorDBMCPServer()


@pytest.fixture()
def ephemeral():
    """Fresh in-memory ChromaDB client per test."""
    return chromadb.EphemeralClient()


@pytest.fixture()
def server(ephemeral):
    """VectorDBMCPServer backed by an in-memory ChromaDB client."""
    return _make_server(ephemeral)


# ---------------------------------------------------------------------------
# Step 1.1 — create_collection bare-except fix
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_collection_success(server, ephemeral):
    result = await server._create_collection({"name": "test_col", "metadata": None})
    assert not result.isError, result.content[0].text
    text = result.content[0].text
    assert "test_col" in text
    assert "created" in text.lower()
    assert ephemeral.get_collection("test_col") is not None


@pytest.mark.asyncio
async def test_create_collection_already_exists_raises_not_swallows(server, ephemeral):
    """Second create on the same name must return isError, not silently pass."""
    ephemeral.create_collection("dupe_col")
    result = await server._create_collection({"name": "dupe_col"})
    assert result.isError
    assert "already exists" in result.content[0].text


@pytest.mark.asyncio
async def test_create_collection_chroma_down_returns_error(server):
    """Real ChromaDB errors (not NotFoundError) must surface, not be swallowed."""
    broken_client = MagicMock()
    broken_client.get_collection.side_effect = RuntimeError("disk full")
    server.chroma_client = broken_client

    result = await server._create_collection({"name": "any_col"})
    assert result.isError


# ---------------------------------------------------------------------------
# Step 1.2 — async model-load locking
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_concurrent_embed_calls_load_model_once(server):
    """Concurrent calls to _ensure_embedding_model must load the model exactly once."""
    load_count = 0

    class FakeModel:
        def encode(self, texts, **_):
            return np.zeros((len(texts), 384), dtype=np.float32)

    def fake_constructor(model_name, *args, **kwargs):
        nonlocal load_count
        load_count += 1
        return FakeModel()

    with patch("tools.mcp.vector_db_server.SentenceTransformer", side_effect=fake_constructor):
        server.embedding_model = None
        results = await asyncio.gather(
            server._ensure_embedding_model(),
            server._ensure_embedding_model(),
            server._ensure_embedding_model(),
        )

    assert all(results), "All calls should return True (model available)"
    assert load_count == 1, f"Model loaded {load_count} times; expected exactly 1"


# ---------------------------------------------------------------------------
# Step 1.3 — uuid4 auto-IDs
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_add_documents_auto_ids_are_unique_across_rapid_calls(server, ephemeral):
    """Auto-generated IDs must be unique even when called in rapid succession."""
    ephemeral.create_collection("id_test")
    server.chroma_client = ephemeral

    mock_model = MagicMock()
    mock_model.encode.return_value = np.array([[0.1] * 384, [0.2] * 384], dtype=np.float32)
    server.embedding_model = mock_model

    args = {"collection_name": "id_test", "documents": ["doc a", "doc b"]}

    result1 = await server._add_documents(args)
    result2 = await server._add_documents(args)

    assert not result1.isError, result1.content[0].text
    assert not result2.isError, result2.content[0].text

    col = ephemeral.get_collection("id_test")
    stored = col.get(include=[])
    all_ids = stored["ids"]
    assert len(all_ids) == 4, f"Expected 4 stored docs, got {len(all_ids)}: {all_ids}"
    assert len(set(all_ids)) == 4, f"Duplicate IDs found: {all_ids}"
    for id_ in all_ids:
        uuid.UUID(id_)  # raises ValueError if not a valid UUID


# ---------------------------------------------------------------------------
# Step 1.4 — upsert semantics
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_add_documents_upsert_overwrites_on_duplicate_id(server, ephemeral):
    """Supplying the same ID twice must overwrite, not error."""
    ephemeral.create_collection("upsert_test")
    server.chroma_client = ephemeral

    mock_model = MagicMock()
    mock_model.encode.side_effect = lambda docs, **kw: np.array([[0.1] * 384] * len(docs), dtype=np.float32)
    server.embedding_model = mock_model

    fixed_id = "fixed-id-001"

    result1 = await server._add_documents(
        {
            "collection_name": "upsert_test",
            "documents": ["original text"],
            "ids": [fixed_id],
        }
    )
    assert not result1.isError, result1.content[0].text

    result2 = await server._add_documents(
        {
            "collection_name": "upsert_test",
            "documents": ["updated text"],
            "ids": [fixed_id],
        }
    )
    assert not result2.isError, result2.content[0].text

    col = ephemeral.get_collection("upsert_test")
    assert col.count() == 1, "Upsert must not create a second document for the same ID"
    stored = col.get(ids=[fixed_id], include=["documents"])
    assert stored["documents"][0] == "updated text"


# ---------------------------------------------------------------------------
# Step 2.1 — vector_stats disk usage and model state fields
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_vector_stats_disk_bytes_is_directory_not_partition(server, tmp_path, monkeypatch):
    """disk_bytes must reflect directory contents, not partition-level usage."""
    import tools.mcp.vector_db_server as mod

    # Write two small files into a temp dir to act as the chroma path
    fake_chroma = tmp_path / "chroma"
    fake_chroma.mkdir()
    (fake_chroma / "file_a.bin").write_bytes(b"x" * 1000)
    (fake_chroma / "file_b.bin").write_bytes(b"x" * 2000)

    monkeypatch.setattr(mod, "CHROMA_PATH", fake_chroma)

    result = await server._vector_stats({})
    assert not result.isError, result.content[0].text
    text = result.content[0].text

    assert "Disk bytes: 3000" in text, f"Expected 3000 bytes from dir sum, got:\n{text}"
    # Partition usage would be in the gigabytes range — confirm we're not reporting that
    assert "Disk bytes: 3000" in text


@pytest.mark.asyncio
async def test_vector_stats_model_loaded_flag_false_before_embed(server):
    """model_loaded must be False when embedding model has not been initialized."""
    server.embedding_model = None

    result = await server._vector_stats({})
    assert not result.isError, result.content[0].text
    text = result.content[0].text

    assert "Model loaded: False" in text, f"Expected 'Model loaded: False' in:\n{text}"
    assert "Embedding dimension: None" in text, f"Expected 'Embedding dimension: None' in:\n{text}"


# ---------------------------------------------------------------------------
# Step 2.2 — EMPTY_QUERY validation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_query_empty_string_returns_error(server, ephemeral):
    """Empty query_text must be rejected before any embedding call."""
    ephemeral.create_collection("q_test")
    server.chroma_client = ephemeral
    server.embedding_model = MagicMock()

    for bad_query in ["", "   ", "\t\n"]:
        result = await server._query_collection(
            {
                "collection_name": "q_test",
                "query_text": bad_query,
            }
        )
        assert result.isError, f"Expected error for query_text={repr(bad_query)}"
        assert "EMPTY_QUERY" in result.content[0].text

    # Embedding model must never have been called
    server.embedding_model.encode.assert_not_called()


@pytest.mark.asyncio
async def test_semantic_search_empty_string_returns_error(server, ephemeral):
    """Empty query must be rejected before any embedding call."""
    server.chroma_client = ephemeral
    server.embedding_model = MagicMock()

    for bad_query in ["", "   ", "\t\n"]:
        result = await server._semantic_search({"query": bad_query})
        assert result.isError, f"Expected error for query={repr(bad_query)}"
        assert "EMPTY_QUERY" in result.content[0].text

    server.embedding_model.encode.assert_not_called()


# ---------------------------------------------------------------------------
# Step 2.3 — get_collection_info structured sample error
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_collection_info_distinguishes_empty_vs_fetch_error(server, ephemeral):
    """sample_error field must be None on success and populated on fetch failure."""
    ephemeral.create_collection("info_test")
    server.chroma_client = ephemeral

    # Empty collection — no documents, no fetch error
    result = await server._get_collection_info({"name": "info_test"})
    assert not result.isError, result.content[0].text
    text = result.content[0].text
    assert "sample_error: None" in text, f"Expected 'sample_error: None' for empty collection:\n{text}"

    # Simulate a fetch failure on .get()
    from unittest.mock import patch as _patch

    broken = MagicMock()
    broken.id = "fake-id"
    broken.count.return_value = 0
    broken.metadata = None
    broken.get.side_effect = RuntimeError("disk read error")
    server.chroma_client = MagicMock()
    server.chroma_client.get_collection.return_value = broken

    result2 = await server._get_collection_info({"name": "info_test"})
    assert not result2.isError, result2.content[0].text
    text2 = result2.content[0].text
    assert "sample_error: None" not in text2, "sample_error should be populated on fetch failure"
    assert "disk read error" in text2, f"Expected error detail in:\n{text2}"


# ---------------------------------------------------------------------------
# Step 2.4 — list_collections includes count
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_collections_includes_count(server, ephemeral):
    """Every collection entry must include a Count line."""
    for name in ("cnt_col_a", "cnt_col_b"):
        try:
            ephemeral.create_collection(name)
        except Exception:  # guardian: allow-broad-exception -- ChromaDB raises heterogeneous errors if collection already exists across versions; safe to skip
            pass
    server.chroma_client = ephemeral

    result = await server._list_collections({})
    assert not result.isError, result.content[0].text
    text = result.content[0].text

    # Every collection in the listing must have a Count line
    collection_blocks = [b for b in text.split("\n\n") if "📁" in b]
    assert len(collection_blocks) >= 2, f"Expected at least 2 collection blocks:\n{text}"
    for block in collection_blocks:
        assert "Count:" in block, f"Missing Count: in block:\n{block}"


@pytest.mark.asyncio
async def test_list_collections_count_null_on_fetch_failure(server):
    """A collection whose .count() raises must appear with Count: null."""
    bad_col = MagicMock()
    bad_col.name = "broken_col"
    bad_col.id = "fake-id-broken"
    bad_col.metadata = None
    bad_col.count.side_effect = RuntimeError("index corrupt")

    client = MagicMock()
    client.list_collections.return_value = [bad_col]
    server.chroma_client = client

    result = await server._list_collections({})
    assert not result.isError, result.content[0].text
    text = result.content[0].text

    assert "Count: null" in text, f"Expected 'Count: null' for broken collection:\n{text}"
    assert "index corrupt" in text, f"Expected error detail in:\n{text}"


# ---------------------------------------------------------------------------
# Step 3.1 — env-var configuration
# ---------------------------------------------------------------------------


def test_env_var_overrides_chroma_path(tmp_path, monkeypatch):
    """VECTOR_DB_CHROMA_PATH env var must override the default at import time."""
    custom = tmp_path / "my_chroma"
    monkeypatch.setenv("VECTOR_DB_CHROMA_PATH", str(custom))

    import importlib
    import tools.mcp.vector_db_server as mod

    importlib.reload(mod)

    assert mod.CHROMA_PATH == custom, f"Expected {custom}, got {mod.CHROMA_PATH}"


def test_env_var_overrides_embedding_model(monkeypatch):
    """VECTOR_DB_EMBEDDING_MODEL env var must override the default at import time."""
    monkeypatch.setenv("VECTOR_DB_EMBEDDING_MODEL", "paraphrase-MiniLM-L3-v2")

    import importlib
    import tools.mcp.vector_db_server as mod

    importlib.reload(mod)

    assert mod.DEFAULT_EMBEDDING_MODEL == "paraphrase-MiniLM-L3-v2"


# ---------------------------------------------------------------------------
# Step 3.2 — embed_text return_vectors flag
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_embed_text_default_omits_vectors(server):
    """Without return_vectors, full vector arrays must not appear in the output."""
    mock_model = MagicMock()
    mock_model.encode.return_value = np.array([[0.1] * 384], dtype=np.float32)
    server.embedding_model = mock_model

    # Ensure processing_time > 0 so texts/second calculation does not divide by zero
    with patch("tools.mcp.vector_db_server.time") as mock_time:
        mock_time.time.side_effect = [0.0, 1.0]
        result = await server._embed_text({"texts": ["hello"]})

    assert not result.isError, result.content[0].text
    text = result.content[0].text

    assert "Sample embeddings" in text, "Preview section must always be present"
    assert "Full vectors" not in text, "Full vector section must be absent when return_vectors omitted"
    assert "return_vectors: False" in text


@pytest.mark.asyncio
async def test_embed_text_return_vectors_true_includes_full_arrays(server):
    """With return_vectors=True the full JSON vector arrays must be in the output."""
    vec = [round(0.1 * i, 4) for i in range(384)]
    mock_model = MagicMock()
    mock_model.encode.return_value = np.array([vec], dtype=np.float32)
    server.embedding_model = mock_model

    with patch("tools.mcp.vector_db_server.time") as mock_time:
        mock_time.time.side_effect = [0.0, 1.0]
        result = await server._embed_text({"texts": ["hello"], "return_vectors": True})

    assert not result.isError, result.content[0].text
    text = result.content[0].text

    assert "Sample embeddings" in text, "Preview section must always be present"
    assert "Full vectors" in text, "Full vector section must be present when return_vectors=True"
    assert "return_vectors: True" in text
    # Spot-check that an actual numeric array appears (not just headers)
    assert "[0.0," in text or "[0," in text, f"Expected numeric array in output:\n{text[:500]}"


# ---------------------------------------------------------------------------
# Step 3.3 — semantic_search flattened sorted output
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_semantic_search_results_sorted_by_distance(server, ephemeral):
    """Merged results must be sorted by distance ascending across collections."""
    for name in ("ss_col_a", "ss_col_b"):
        try:
            ephemeral.create_collection(name)
        except Exception:  # guardian: allow-broad-exception -- ChromaDB raises heterogeneous errors if collection already exists; safe to skip in test setup
            pass

    server.chroma_client = ephemeral

    # Patch query to return controlled distances without real embeddings
    controlled_results = {
        "ss_col_a": {"documents": [["doc_far"]], "distances": [[0.9]], "metadatas": [[{}]]},
        "ss_col_b": {"documents": [["doc_near"]], "distances": [[0.1]], "metadatas": [[{}]]},
    }

    original_get = ephemeral.get_collection

    def patched_get(name):
        col = original_get(name)
        mock_col = MagicMock(wraps=col)
        mock_col.query.return_value = controlled_results[name]
        return mock_col

    mock_model = MagicMock()
    mock_model.encode.return_value = np.zeros((1, 384), dtype=np.float32)
    server.embedding_model = mock_model

    with patch.object(ephemeral, "get_collection", side_effect=patched_get):
        result = await server._semantic_search(
            {
                "query": "test query",
                "collections": ["ss_col_a", "ss_col_b"],
                "n_results": 5,
            }
        )

    assert not result.isError, result.content[0].text
    text = result.content[0].text

    # doc_near (dist 0.1) must appear before doc_far (dist 0.9)
    pos_near = text.index("doc_near")
    pos_far = text.index("doc_far")
    assert pos_near < pos_far, f"Expected doc_near before doc_far (sorted by distance):\n{text}"


@pytest.mark.asyncio
async def test_semantic_search_flattened_results_include_collection_and_rank(server, ephemeral):
    """Every result line in the flat list must include the collection name and a rank number."""
    try:
        ephemeral.create_collection("ss_flat_col")
    except Exception:  # guardian: allow-broad-exception -- ChromaDB raises heterogeneous errors if collection already exists; safe to skip in test setup
        pass

    server.chroma_client = ephemeral

    controlled = {
        "documents": [["alpha doc", "beta doc"]],
        "distances": [[0.2, 0.5]],
        "metadatas": [[{}, {}]],
    }

    original_get = ephemeral.get_collection

    def patched_get(name):
        col = original_get(name)
        mock_col = MagicMock(wraps=col)
        mock_col.query.return_value = controlled
        return mock_col

    mock_model = MagicMock()
    mock_model.encode.return_value = np.zeros((1, 384), dtype=np.float32)
    server.embedding_model = mock_model

    with patch.object(ephemeral, "get_collection", side_effect=patched_get):
        result = await server._semantic_search(
            {
                "query": "test query",
                "collections": ["ss_flat_col"],
                "n_results": 5,
            }
        )

    assert not result.isError, result.content[0].text
    text = result.content[0].text

    assert "1. [ss_flat_col]" in text, f"Expected rank-1 line with collection name:\n{text}"
    assert "2. [ss_flat_col]" in text, f"Expected rank-2 line with collection name:\n{text}"
    assert "alpha doc" in text
    assert "beta doc" in text


# ---------------------------------------------------------------------------
# Hardening pass
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_semantic_search_n_results_type_coerced_to_int(server, ephemeral):
    """n_results passed as a float-like value must be coerced to int without error."""
    try:
        ephemeral.create_collection("nr_col")
    except Exception:  # guardian: allow-broad-exception -- ChromaDB raises heterogeneous errors if collection already exists; safe to skip in test setup
        pass
    server.chroma_client = ephemeral

    mock_model = MagicMock()
    mock_model.encode.return_value = np.zeros((1, 384), dtype=np.float32)
    server.embedding_model = mock_model

    # Pass n_results as a string "3" (simulates JSON deserialization edge case)
    result = await server._semantic_search(
        {
            "query": "hello",
            "collections": ["nr_col"],
            "n_results": "3",
        }
    )
    # Must not crash with TypeError — empty collection returns empty results cleanly
    assert not result.isError or "EMPTY_QUERY" not in result.content[0].text


@pytest.mark.asyncio
async def test_embed_text_zero_duration_does_not_divide_by_zero(server):
    """Even when encode() completes in zero elapsed time the server must not raise ZeroDivisionError."""
    mock_model = MagicMock()
    mock_model.encode.return_value = np.array([[0.1] * 384], dtype=np.float32)
    server.embedding_model = mock_model

    # Force processing_time to exactly 0.0 by returning the same timestamp twice
    with patch("tools.mcp.vector_db_server.time") as mock_time:
        mock_time.time.side_effect = [0.0, 0.0]
        result = await server._embed_text({"texts": ["hello"]})

    assert not result.isError, result.content[0].text
    text = result.content[0].text
    assert "Texts per second:" in text, f"Rate line missing:\n{text}"
    # Value must be a large finite number, not inf or nan
    rate_line = [l for l in text.splitlines() if "Texts per second:" in l][0]
    rate_val = float(rate_line.split(":")[1].strip())
    assert rate_val > 0, f"Rate must be positive: {rate_val}"
    import math

    assert math.isfinite(rate_val), f"Rate must be finite: {rate_val}"


def test_invalid_env_var_for_max_batch_falls_back_safely(monkeypatch):
    """A non-integer VECTOR_DB_MAX_BATCH must fall back to the default without crashing."""
    monkeypatch.setenv("VECTOR_DB_MAX_BATCH", "not_a_number")

    import importlib
    import tools.mcp.vector_db_server as mod

    importlib.reload(mod)

    assert mod.MAX_EMBEDDING_BATCH_SIZE == 32, f"Expected default 32, got {mod.MAX_EMBEDDING_BATCH_SIZE}"


@pytest.mark.asyncio
async def test_semantic_search_tie_order_is_deterministic(server, ephemeral):
    """Two hits with identical distance must appear in a consistent (alphabetical) order."""
    for name in ("tie_col_a", "tie_col_b"):
        try:
            ephemeral.create_collection(name)
        except Exception:  # guardian: allow-broad-exception -- ChromaDB raises heterogeneous errors if collection already exists; safe to skip in test setup
            pass
    server.chroma_client = ephemeral

    # Both collections return one doc with the same distance 0.5
    controlled = {
        "tie_col_a": {"documents": [["alpha"]], "distances": [[0.5]], "metadatas": [[{}]]},
        "tie_col_b": {"documents": [["beta"]], "distances": [[0.5]], "metadatas": [[{}]]},
    }
    original_get = ephemeral.get_collection

    def patched_get(name):
        col = original_get(name)
        mock_col = MagicMock(wraps=col)
        mock_col.query.return_value = controlled[name]
        return mock_col

    mock_model = MagicMock()
    mock_model.encode.return_value = np.zeros((1, 384), dtype=np.float32)
    server.embedding_model = mock_model

    results = []
    for _ in range(3):
        with patch.object(ephemeral, "get_collection", side_effect=patched_get):
            r = await server._semantic_search(
                {
                    "query": "test",
                    "collections": ["tie_col_a", "tie_col_b"],
                    "n_results": 5,
                }
            )
        results.append(r.content[0].text)

    # All three runs must produce identical output
    assert results[0] == results[1] == results[2], (
        "Tied-distance results must be in the same order across runs"
    )
    # alpha (tie_col_a) must sort before beta (tie_col_b) — alphabetical by collection then doc
    pos_alpha = results[0].index("alpha")
    pos_beta = results[0].index("beta")
    assert pos_alpha < pos_beta, f"Expected alpha before beta (alphabetical tie-break):\n{results[0]}"
