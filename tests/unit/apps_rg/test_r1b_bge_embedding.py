"""R1B uses BGE vectors when embeddings bootstrap is active."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from apps_rg.cache.r1b_bge_embedding import (
    embed_texts_bge,
    intent_vector_payload,
    reset_bge_model_for_testing,
    resolve_query_vector,
)
from apps_rg.runtime.embedding_settings import (
    AppsRgEmbeddingFailClosedError,
    bootstrap_apps_rg_embedding_env,
)


@pytest.fixture(autouse=True)
def _reset_model() -> None:
    reset_bge_model_for_testing()
    yield
    reset_bge_model_for_testing()


def test_intent_vector_payload_uses_bge_when_model_available(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    snap = tmp_path / "hub" / "models--BAAI--bge-m3" / "snapshots" / "abc"
    snap.mkdir(parents=True)
    (snap / "config.json").write_text("{}", encoding="utf-8")
    monkeypatch.setenv("HF_HOME", str(tmp_path))
    bootstrap_apps_rg_embedding_env(repo_root=tmp_path)

    fake = MagicMock()
    fake.encode.return_value = np.ones((1, 1024), dtype=np.float32)
    with patch("apps_rg.cache.r1b_bge_embedding._get_bge_model", return_value=fake):
        payload = intent_vector_payload(intent_text="apps_rg|role|acme|svp", digest="abc")
    assert payload["embedding_model"] == "BAAI/bge-m3"
    assert payload["dimensions"] == 1024
    assert len(payload["values"]) == 1024


def test_embed_texts_bge_batches_non_empty_texts_preserving_order() -> None:
    fake = MagicMock()
    fake.encode.return_value = np.array(
        [
            np.full((1024,), 1.0, dtype=np.float32),
            np.full((1024,), 2.0, dtype=np.float32),
        ],
        dtype=np.float32,
    )

    with patch("apps_rg.cache.r1b_bge_embedding._get_bge_model", return_value=fake):
        vectors = embed_texts_bge([" parent ", " ", "child"], batch_size=2)

    fake.encode.assert_called_once_with(
        ["parent", "child"],
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
        batch_size=2,
    )
    assert vectors[0] is not None
    assert vectors[1] is None
    assert vectors[2] is not None
    assert vectors[0][0] == 1.0
    assert vectors[2][0] == 2.0
    assert len(vectors[0]) == 1024
    assert len(vectors[2]) == 1024


def test_resolve_query_vector_falls_back_without_bge(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_TEST_HARNESS", "1")
    monkeypatch.setenv("EMBEDDING_ENABLED", "false")
    monkeypatch.setenv("HF_HOME", "/nonexistent")
    with patch("apps_rg.cache.r1b_bge_embedding.embed_text_bge", return_value=None):
        vec, kind = resolve_query_vector("apps_rg|role|x|y", "deadbeef" * 8)
    assert kind == "pseudo_digest"
    assert len(vec) == 32


def test_resolve_query_vector_fail_closed_on_product_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
    monkeypatch.delenv("APPS_RG_ALLOW_PRODUCT_SHORTCUTS", raising=False)
    monkeypatch.setenv("APPS_RG_WHOLE_RUN_ENVELOPE", "1")
    monkeypatch.setenv("EMBEDDING_ENABLED", "false")
    monkeypatch.setenv("HF_HOME", "/nonexistent")
    with (
        patch("apps_rg.cache.r1b_bge_embedding.embed_text_bge", return_value=None),
        pytest.raises(AppsRgEmbeddingFailClosedError),
    ):
        resolve_query_vector("apps_rg|role|x|y", "deadbeef" * 8)
