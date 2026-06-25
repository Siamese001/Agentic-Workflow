"""Fail-closed apps_rg embedding / BGE / Chroma semantics (no agentic_core edits)."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from apps_rg.runtime.embedding_settings import (
    AppsRgEmbeddingFailClosedError,
    apply_apps_rg_embedding_env_guards,
    bootstrap_apps_rg_embedding_env,
    load_bge_sentence_transformer,
    resolve_apps_rg_embedding_settings,
    semantic_cache_r1b_eligible,
)


@pytest.fixture(autouse=True)
def _clean_embedding_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in (
        "EMBEDDING_ENABLED",
        "APPS_RG_EMBEDDING_ENABLED",
        "CHROMA_PERSIST_DIR",
        "APPS_RG_EMBEDDING_MODEL_PATH",
        "SEMANTIC_CACHE_D2_ENABLED",
        "HF_HUB_OFFLINE",
        "TRANSFORMERS_OFFLINE",
    ):
        monkeypatch.delenv(key, raising=False)


def test_bootstrap_defaults_chroma_and_embedding_without_manual_env(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    (repo / "data" / "cache" / "chromadb").mkdir(parents=True)
    snap = tmp_path / "hub" / "models--BAAI--bge-m3" / "snapshots" / "abc123"
    snap.mkdir(parents=True)
    (snap / "config.json").write_text("{}", encoding="utf-8")
    monkeypatch.setenv("HF_HOME", str(tmp_path))
    monkeypatch.delenv("CHROMA_PERSIST_DIR", raising=False)
    monkeypatch.delenv("EMBEDDING_ENABLED", raising=False)
    monkeypatch.delenv("APPS_RG_EMBEDDING_ENABLED", raising=False)
    applied = bootstrap_apps_rg_embedding_env(repo_root=repo)
    assert "CHROMA_PERSIST_DIR" in applied
    assert applied["EMBEDDING_ENABLED"] == "true"
    assert os.environ["CHROMA_PERSIST_DIR"] == str((repo / "data" / "cache" / "chromadb").resolve())
    assert os.environ.get("EMBEDDING_ENABLED") == "true"


def test_bootstrap_enables_bge_when_hf_snapshot_present(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    snap = tmp_path / "hub" / "models--BAAI--bge-m3" / "snapshots" / "abc123"
    snap.mkdir(parents=True)
    (snap / "config.json").write_text("{}", encoding="utf-8")
    monkeypatch.setenv("HF_HOME", str(tmp_path))
    monkeypatch.delenv("EMBEDDING_ENABLED", raising=False)
    monkeypatch.delenv("APPS_RG_EMBEDDING_ENABLED", raising=False)
    monkeypatch.delenv("APPS_RG_EMBEDDING_MODEL_PATH", raising=False)
    applied = bootstrap_apps_rg_embedding_env(repo_root=tmp_path)
    assert applied.get("EMBEDDING_ENABLED") == "true"
    assert applied.get("APPS_RG_EMBEDDING_MODEL_PATH") == str(snap.resolve())
    s = resolve_apps_rg_embedding_settings()
    assert s.embeddings_enabled is True
    assert s.embedding_model_resolved is True


def test_bootstrap_respects_explicit_disable(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    snap = tmp_path / "hub" / "models--BAAI--bge-m3" / "snapshots" / "abc123"
    snap.mkdir(parents=True)
    (snap / "config.json").write_text("{}", encoding="utf-8")
    monkeypatch.setenv("HF_HOME", str(tmp_path))
    monkeypatch.setenv("EMBEDDING_ENABLED", "false")
    applied = bootstrap_apps_rg_embedding_env(repo_root=tmp_path)
    assert "EMBEDDING_ENABLED" not in applied
    s = resolve_apps_rg_embedding_settings()
    assert s.embeddings_enabled is False


def test_embeddings_disabled_marks_r1b_ineligible_and_disables_d2(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EMBEDDING_ENABLED", "false")
    monkeypatch.setenv("SEMANTIC_CACHE_D2_ENABLED", "1")
    s = apply_apps_rg_embedding_env_guards()
    assert s.embeddings_enabled is False
    assert s.semantic_cache_ineligible is True
    assert s.dense_retrieval_ineligible is True
    assert s.chroma_default_ef_used is False
    assert os.environ.get("SEMANTIC_CACHE_D2_ENABLED") == "0"
    assert os.environ.get("APPS_RG_EMBEDDING_PROVIDER") == "bge_local"
    assert os.environ.get("APPS_RG_FORBID_CHROMA_DEFAULT_EF") == "1"
    assert semantic_cache_r1b_eligible(s) is False


def test_embeddings_disabled_chroma_configured_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EMBEDDING_ENABLED", "0")
    monkeypatch.setenv("CHROMA_PERSIST_DIR", "/tmp/chroma_test")
    s = resolve_apps_rg_embedding_settings()
    assert s.route_result == "FAIL_CLOSED"
    assert s.embedding_required is True
    assert s.chroma_default_ef_used is False


def test_embeddings_disabled_does_not_load_sentence_transformer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("EMBEDDING_ENABLED", "false")
    s = resolve_apps_rg_embedding_settings()
    with patch("sentence_transformers.SentenceTransformer") as st_mock:
        with pytest.raises(AppsRgEmbeddingFailClosedError):
            load_bge_sentence_transformer(s)
    st_mock.assert_not_called()


def test_embeddings_enabled_missing_local_bge_fail_closed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("EMBEDDING_ENABLED", "true")
    monkeypatch.setenv("CHROMA_PERSIST_DIR", "/tmp/chroma_test")
    monkeypatch.setenv("HF_HOME", str(tmp_path / "empty_hf"))
    monkeypatch.delenv("APPS_RG_EMBEDDING_MODEL_PATH", raising=False)
    s = resolve_apps_rg_embedding_settings()
    assert s.embeddings_enabled is True
    assert s.embedding_model_resolved is False
    assert s.route_result == "FAIL_CLOSED"
    assert s.chroma_default_ef_used is False


def test_embeddings_enabled_local_bge_uses_explicit_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    model_dir = tmp_path / "bge"
    model_dir.mkdir()
    (model_dir / "config.json").write_text("{}", encoding="utf-8")
    monkeypatch.setenv("EMBEDDING_ENABLED", "true")
    monkeypatch.setenv("APPS_RG_EMBEDDING_MODEL_PATH", str(model_dir))
    monkeypatch.setenv("EMBEDDING_DEVICE", "cpu")
    s = resolve_apps_rg_embedding_settings()
    assert s.embedding_model_resolved is True
    assert s.embedding_model_source == "local"
    assert s.chroma_default_ef_used is False

    fake_model = MagicMock()
    with patch("sentence_transformers.SentenceTransformer", return_value=fake_model) as st_mock:
        loaded = load_bge_sentence_transformer(s)
    assert loaded is fake_model
    st_mock.assert_called_once()
    _args, kwargs = st_mock.call_args
    assert str(_args[0]) == str(model_dir.resolve())
    assert kwargs.get("local_files_only") is True
    assert kwargs.get("device") == "cpu"


def test_c0_binding_get_embedding_model_blocked_when_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("EMBEDDING_ENABLED", "false")
    monkeypatch.setenv("CHROMA_PERSIST_DIR", "/tmp/chroma_test")
    from apps_rg.runtime.bindings import c0_binding

    c0_binding._embedding_singleton = None
    c0_binding._embedding_singleton_path = None
    with patch("sentence_transformers.SentenceTransformer") as st_mock:
        with pytest.raises(Exception):
            c0_binding._get_embedding_model()
    st_mock.assert_not_called()


def test_whole_run_preflight_skips_r1b_when_embeddings_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("EMBEDDING_ENABLED", "false")
    apply_apps_rg_embedding_env_guards()
    from apps_rg.cache.whole_run_entrypoint_preflight import _semantic_cache_r1b_enabled

    assert _semantic_cache_r1b_enabled() is False


def test_invalid_slug_bge_m3_v1_maps_to_canonical_without_hf_lookup(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("EMBEDDING_ENABLED", "true")
    monkeypatch.setenv("EMBEDDING_MODEL_ID", "bge-m3-v1")
    pre = tmp_path / "artifacts" / "models" / "BAAI" / "bge-m3"
    pre.mkdir(parents=True)
    (pre / "weights.bin").write_bytes(b"x")
    monkeypatch.setenv("AGENTIC_REPO_ROOT", str(tmp_path))
    s = resolve_apps_rg_embedding_settings()
    assert s.embedding_model_name == "BAAI/bge-m3"
    assert s.embedding_model_resolved is True
