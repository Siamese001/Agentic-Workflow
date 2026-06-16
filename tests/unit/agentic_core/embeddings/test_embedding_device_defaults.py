"""GPU-first embedding device resolver tests."""

from __future__ import annotations

import sys
from types import ModuleType
from unittest.mock import MagicMock, patch


def test_model_loader_defaults_to_shared_bge_device_resolver() -> None:
    from agentic_core.embeddings.model_loader import ModelLoader

    with patch("agentic_core.embeddings.bge_runtime._resolve_device", return_value="cuda"):
        loader = ModelLoader()

    assert loader._device == "cuda"


def test_model_loader_explicit_device_wins() -> None:
    from agentic_core.embeddings.model_loader import ModelLoader

    with patch("agentic_core.embeddings.bge_runtime._resolve_device", return_value="cuda"):
        loader = ModelLoader(device="cpu")

    assert loader._device == "cpu"


def test_bge_m3_factory_helper_defaults_to_shared_device_resolver(monkeypatch) -> None:
    from agentic_core.embeddings.embedding_factory import _create_bge_m3_client

    fake_model = MagicMock()
    fake_model.get_sentence_embedding_dimension.return_value = 1024
    fake_sentence_transformers = ModuleType("sentence_transformers")
    fake_sentence_transformers.SentenceTransformer = MagicMock(return_value=fake_model)
    monkeypatch.setitem(sys.modules, "sentence_transformers", fake_sentence_transformers)

    with patch("agentic_core.embeddings.bge_runtime._resolve_device", return_value="cuda"):
        _create_bge_m3_client("fake-bge")

    fake_sentence_transformers.SentenceTransformer.assert_called_once()
    assert fake_sentence_transformers.SentenceTransformer.call_args.kwargs["device"] == "cuda"
