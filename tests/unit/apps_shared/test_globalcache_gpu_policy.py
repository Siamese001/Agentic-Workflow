"""GPU policy coverage for apps_shared GlobalCache vector helpers."""

from __future__ import annotations

import sys
import types
from typing import Any

import numpy as np
import pytest

# apps-test-model: HARNESS


def test_simple_embedder_defaults_to_cpu(monkeypatch: pytest.MonkeyPatch) -> None:
    from apps_shared.enforcement import GlobalcacheStrategy as m

    captured: dict[str, Any] = {}

    class FakeSentenceTransformer:
        def __init__(self, model_name: str, **kwargs: Any) -> None:
            captured["model_name"] = model_name
            captured["kwargs"] = kwargs

    monkeypatch.delenv("APPS_SHARED_VECTOR_GPU_ENABLED", raising=False)
    with pytest.MonkeyPatch.context() as mp:
        mp.setitem(
            sys.modules,
            "sentence_transformers",
            types.SimpleNamespace(SentenceTransformer=FakeSentenceTransformer),
        )
        embedder = m.SimpleEmbedder()
        embedder._load_model()

    assert captured["model_name"] == m.BGE_M3_MODEL_ID
    assert captured["kwargs"]["device"] == "cpu"


def test_simple_embedder_uses_cuda_only_when_opted_in(monkeypatch: pytest.MonkeyPatch) -> None:
    from apps_shared.enforcement import GlobalcacheStrategy as m

    captured: dict[str, Any] = {}

    class FakeSentenceTransformer:
        def __init__(self, model_name: str, **kwargs: Any) -> None:
            captured["model_name"] = model_name
            captured["kwargs"] = kwargs

    monkeypatch.setenv("APPS_SHARED_VECTOR_GPU_ENABLED", "1")
    monkeypatch.setenv("APPS_SHARED_EMBEDDING_DEVICE", "cuda")
    with pytest.MonkeyPatch.context() as mp:
        mp.setitem(
            sys.modules,
            "sentence_transformers",
            types.SimpleNamespace(SentenceTransformer=FakeSentenceTransformer),
        )
        embedder = m.SimpleEmbedder()
        embedder._load_model()

    assert captured["model_name"] == m.BGE_M3_MODEL_ID
    assert captured["kwargs"]["device"] == "cuda"


def test_l2_vector_store_keeps_small_sets_on_cpu(monkeypatch: pytest.MonkeyPatch) -> None:
    from apps_shared.enforcement import GlobalcacheStrategy as m

    monkeypatch.setenv("APPS_SHARED_VECTOR_GPU_ENABLED", "1")
    monkeypatch.setenv("APPS_SHARED_VECTOR_GPU_MIN_ROWS", "3")
    store = m.L2VectorStore(max_size=10)
    store.add(m.CacheEntry(key_hash="a", value="A", embedding=[1.0, 0.0]))
    store.add(m.CacheEntry(key_hash="b", value="B", embedding=[0.0, 1.0]))

    results = store.search([1.0, 0.0], threshold=0.5, max_results=1)

    assert [(entry.value, score) for entry, score in results] == [("A", 1.0)]
    assert store.get_stats()["similarity_backend"] == "cpu_numpy"
    assert store.get_stats()["gpu_enabled"] is False


def test_l2_vector_store_uses_cuda_when_opted_in_and_threshold_met(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from apps_shared.enforcement import GlobalcacheStrategy as m

    calls: list[tuple[tuple[int, ...], list[float]]] = []

    def fake_cuda_dot(embeddings: np.ndarray, query_vec: np.ndarray) -> np.ndarray:
        calls.append((embeddings.shape, query_vec.tolist()))
        return np.array([0.95, 0.10])

    monkeypatch.setenv("APPS_SHARED_VECTOR_GPU_ENABLED", "1")
    monkeypatch.setenv("APPS_SHARED_VECTOR_GPU_MIN_ROWS", "1")
    monkeypatch.setattr(m, "_torch_cuda_dot", fake_cuda_dot)
    store = m.L2VectorStore(max_size=10)
    store.add(m.CacheEntry(key_hash="a", value="A", embedding=[1.0, 0.0]))
    store.add(m.CacheEntry(key_hash="b", value="B", embedding=[0.0, 1.0]))

    results = store.search([1.0, 0.0], threshold=0.5, max_results=1)

    assert calls == [((2, 2), [1.0, 0.0])]
    assert [(entry.value, score) for entry, score in results] == [("A", 0.95)]
    assert store.get_stats()["similarity_backend"] == "cuda_torch"
    assert store.get_stats()["gpu_enabled"] is True


def test_l2_vector_store_falls_back_to_cpu_when_cuda_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from apps_shared.enforcement import GlobalcacheStrategy as m

    monkeypatch.setenv("APPS_SHARED_VECTOR_GPU_ENABLED", "1")
    monkeypatch.setenv("APPS_SHARED_VECTOR_GPU_MIN_ROWS", "1")
    monkeypatch.setattr(m, "_torch_cuda_dot", lambda _embeddings, _query_vec: None)
    store = m.L2VectorStore(max_size=10)
    store.add(m.CacheEntry(key_hash="a", value="A", embedding=[1.0, 0.0]))
    store.add(m.CacheEntry(key_hash="b", value="B", embedding=[0.0, 1.0]))

    results = store.search([1.0, 0.0], threshold=0.5, max_results=1)

    assert [(entry.value, score) for entry, score in results] == [("A", 1.0)]
    assert store.get_stats()["similarity_backend"] == "cpu_numpy"
    assert store.get_stats()["gpu_enabled"] is True
