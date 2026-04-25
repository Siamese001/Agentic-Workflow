"""Behavioral tests for ``agentic_core.L4_state.utils.client.chroma_client.SovereignChromaClient``.

Covers:
- ``_sanitize_metadata`` coercion rules for ChromaDB v2 scalar-only values.
- ``embed_texts`` empty-input short-circuit and EMBEDDING_ENABLED gate.
- Collection caching: same instance returned on repeat ``get_collection``.
- ``add_documents`` validation: doc/metadata length mismatch, id length mismatch.
- ``query`` delegates to collection.query with sanitized embeddings.
- ``get_collection_stats`` returns expected shape.
- ``list_collections`` delegates to client.
- ``delete_collection`` removes from cache on success and re-raises on failure.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def client(tmp_path: Path):
    """Build a client with a mocked chromadb.PersistentClient."""
    from agentic_core.L4_state.utils.client import chroma_client as mod

    with patch.object(mod.chromadb, "PersistentClient") as mock_pc:
        mock_backend = MagicMock()
        mock_pc.return_value = mock_backend
        instance = mod.SovereignChromaClient(persist_dir=str(tmp_path / "chroma"))
        instance._mock_backend = mock_backend  # expose for tests  # type: ignore[attr-defined]
        yield instance


# ---- _sanitize_metadata --------------------------------------------------


class TestSanitizeMetadata:
    def test_scalar_types_preserved(self) -> None:
        from agentic_core.L4_state.utils.client.chroma_client import SovereignChromaClient

        out = SovereignChromaClient._sanitize_metadata(
            {"s": "x", "i": 1, "f": 1.5, "b": True},
        )
        assert out == {"s": "x", "i": 1, "f": 1.5, "b": True}

    def test_none_becomes_empty_string(self) -> None:
        from agentic_core.L4_state.utils.client.chroma_client import SovereignChromaClient

        out = SovereignChromaClient._sanitize_metadata({"k": None})
        assert out == {"k": ""}

    def test_list_json_encoded(self) -> None:
        from agentic_core.L4_state.utils.client.chroma_client import SovereignChromaClient

        out = SovereignChromaClient._sanitize_metadata({"tags": ["a", "b"]})
        assert out["tags"] == '["a", "b"]'

    def test_dict_json_encoded_sorted(self) -> None:
        from agentic_core.L4_state.utils.client.chroma_client import SovereignChromaClient

        out = SovereignChromaClient._sanitize_metadata({"nested": {"b": 2, "a": 1}})
        assert out["nested"] == '{"a": 1, "b": 2}'

    def test_tuple_json_encoded(self) -> None:
        from agentic_core.L4_state.utils.client.chroma_client import SovereignChromaClient

        out = SovereignChromaClient._sanitize_metadata({"t": (1, 2)})
        assert out["t"] == "[1, 2]"

    def test_other_types_stringified(self) -> None:
        from agentic_core.L4_state.utils.client.chroma_client import SovereignChromaClient

        out = SovereignChromaClient._sanitize_metadata({"p": Path("/x")})
        assert isinstance(out["p"], str)


# ---- embed_texts ---------------------------------------------------------


class TestEmbedTexts:
    def test_empty_short_circuits(self, client: Any) -> None:
        assert client.embed_texts([]) == []

    def test_disabled_raises(
        self,
        client: Any,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.delenv("EMBEDDING_ENABLED", raising=False)
        with pytest.raises(RuntimeError, match="EMBEDDING_ENABLED"):
            client.embed_texts(["hello"])

    @pytest.mark.parametrize("val", ["", "0", "false", "no", "FALSE"])
    def test_non_true_disables(
        self,
        client: Any,
        monkeypatch: pytest.MonkeyPatch,
        val: str,
    ) -> None:
        monkeypatch.setenv("EMBEDDING_ENABLED", val)
        with pytest.raises(RuntimeError, match="EMBEDDING_ENABLED"):
            client.embed_texts(["hello"])

    def test_enabled_delegates_to_bge(
        self,
        client: Any,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("EMBEDDING_ENABLED", "true")
        expected = [[0.1, 0.2], [0.3, 0.4]]
        with patch(
            "agentic_core.embeddings.bge_runtime.bge_embed_batch",
            return_value=expected,
        ) as mock_embed:
            out = client.embed_texts(["a", "b"])
        mock_embed.assert_called_once_with(["a", "b"])
        assert out == expected


# ---- get_collection caching ---------------------------------------------


class TestCollectionCache:
    def test_cache_reuses_collection(self, client: Any) -> None:
        client._mock_backend.get_or_create_collection.return_value = "COL1"
        first = client.get_collection("users")
        second = client.get_collection("users")
        assert first is second
        assert client._mock_backend.get_or_create_collection.call_count == 1

    def test_different_names_are_separate(self, client: Any) -> None:
        client._mock_backend.get_or_create_collection.side_effect = ["C_A", "C_B"]
        assert client.get_collection("a") == "C_A"
        assert client.get_collection("b") == "C_B"
        assert client._mock_backend.get_or_create_collection.call_count == 2


# ---- add_documents validation -------------------------------------------


class TestAddDocumentsValidation:
    def test_mismatched_metadata_length_rejected(self, client: Any) -> None:
        with pytest.raises(ValueError, match="same length"):
            client.add_documents(
                collection_name="c",
                documents=["d1", "d2"],
                metadatas=[{"k": 1}],
            )

    def test_mismatched_ids_length_rejected(
        self,
        client: Any,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("EMBEDDING_ENABLED", "true")
        with pytest.raises(ValueError, match="IDs must match"):
            client.add_documents(
                collection_name="c",
                documents=["d1", "d2"],
                metadatas=[{}, {}],
                ids=["only-one"],
            )

    def test_happy_path_delegates_to_collection(
        self,
        client: Any,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("EMBEDDING_ENABLED", "true")
        fake_collection = MagicMock()
        client._mock_backend.get_or_create_collection.return_value = fake_collection
        embeddings = [[0.1], [0.2]]
        with patch(
            "agentic_core.embeddings.bge_runtime.bge_embed_batch",
            return_value=embeddings,
        ):
            client.add_documents(
                collection_name="c",
                documents=["d1", "d2"],
                metadatas=[{"tags": ["x"]}, {"v": None}],
            )
        fake_collection.add.assert_called_once()
        kwargs = fake_collection.add.call_args.kwargs
        assert kwargs["documents"] == ["d1", "d2"]
        assert kwargs["embeddings"] == embeddings
        # metadata sanitized
        assert kwargs["metadatas"] == [{"tags": '["x"]'}, {"v": ""}]
        # auto-generated ids
        assert kwargs["ids"] == ["doc_0", "doc_1"]

    def test_explicit_ids_pass_through(
        self,
        client: Any,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("EMBEDDING_ENABLED", "true")
        fake_collection = MagicMock()
        client._mock_backend.get_or_create_collection.return_value = fake_collection
        with patch(
            "agentic_core.embeddings.bge_runtime.bge_embed_batch",
            return_value=[[0.1]],
        ):
            client.add_documents(
                collection_name="c",
                documents=["d1"],
                metadatas=[{}],
                ids=["my-id"],
            )
        assert fake_collection.add.call_args.kwargs["ids"] == ["my-id"]


# ---- query ---------------------------------------------------------------


class TestQuery:
    def test_query_delegates(
        self,
        client: Any,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("EMBEDDING_ENABLED", "true")
        fake_collection = MagicMock()
        fake_collection.query.return_value = {"ids": [["a", "b"]], "documents": [["x", "y"]]}
        client._mock_backend.get_or_create_collection.return_value = fake_collection
        with patch(
            "agentic_core.embeddings.bge_runtime.bge_embed_batch",
            return_value=[[0.1, 0.2]],
        ):
            result = client.query(
                collection_name="c",
                query_texts=["hello"],
                n_results=3,
                where={"tag": "x"},
            )
        fake_collection.query.assert_called_once()
        kwargs = fake_collection.query.call_args.kwargs
        assert kwargs["n_results"] == 3
        assert kwargs["where"] == {"tag": "x"}
        assert kwargs["query_embeddings"] == [[0.1, 0.2]]
        assert result["ids"] == [["a", "b"]]


# ---- stats / list / delete ----------------------------------------------


class TestStatsListDelete:
    def test_get_collection_stats(self, client: Any) -> None:
        fake = MagicMock()
        fake.count.return_value = 42
        client._mock_backend.get_or_create_collection.return_value = fake
        stats = client.get_collection_stats("c")
        assert stats["name"] == "c"
        assert stats["document_count"] == 42
        assert "persist_dir" in stats

    def test_list_collections(self, client: Any) -> None:
        client._mock_backend.list_collections.return_value = [
            MagicMock(name="x"),
            MagicMock(name="y"),
        ]
        # MagicMock's .name attribute is special — set explicitly
        client._mock_backend.list_collections.return_value[0].name = "a"
        client._mock_backend.list_collections.return_value[1].name = "b"
        assert client.list_collections() == ["a", "b"]

    def test_delete_removes_from_cache(self, client: Any) -> None:
        client._collections["c"] = "cached"
        client.delete_collection("c")
        assert "c" not in client._collections
        client._mock_backend.delete_collection.assert_called_once_with(name="c")

    def test_delete_reraises_error(self, client: Any) -> None:
        client._mock_backend.delete_collection.side_effect = RuntimeError("boom")
        with pytest.raises(RuntimeError, match="boom"):
            client.delete_collection("c")

    def test_delete_missing_from_cache_ok(self, client: Any) -> None:
        # Collection not in cache — still calls backend, does not raise
        client.delete_collection("never-cached")
        client._mock_backend.delete_collection.assert_called_once_with(
            name="never-cached",
        )
