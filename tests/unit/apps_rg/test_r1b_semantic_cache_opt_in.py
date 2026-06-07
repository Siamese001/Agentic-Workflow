"""R1B terminal semantic output cache is opt-in only."""

from __future__ import annotations

import os
from pathlib import Path

from apps_rg.cache import whole_run_entrypoint_preflight as preflight_mod
from apps_rg.runtime import embedding_settings as emb
from apps_rg.runtime.embedding_settings import AppsRgEmbeddingSettings


def _settings(*, semantic_enabled: bool, model_resolved: bool = True) -> AppsRgEmbeddingSettings:
    return AppsRgEmbeddingSettings(
        embeddings_enabled=True,
        embedding_required=False,
        embedding_model_name="BAAI/bge-m3",
        embedding_model_path="/models/bge-m3" if model_resolved else None,
        embedding_model_resolved=model_resolved,
        embedding_model_source="local" if model_resolved else "unavailable",
        vector_db="chroma",
        semantic_cache_enabled=semantic_enabled,
        dense_retrieval_enabled=True,
        chroma_default_ef_allowed=False,
        chroma_default_ef_used=False,
        failure_mode="not_applicable",
        semantic_cache_ineligible=not model_resolved,
        dense_retrieval_ineligible=False,
        route_result="CONTINUE_WITH_NON_EMBEDDING_PATH",
        decisive_reason="test",
        chroma_persist_dir="/tmp/chroma",
    )


def test_no_env_var_means_r1b_disabled(monkeypatch) -> None:
    monkeypatch.delenv("APPS_RG_ENABLE_R1B_SEMANTIC_CACHE", raising=False)
    assert emb.semantic_cache_r1b_eligible(_settings(semantic_enabled=True)) is False


def test_env_zero_means_r1b_disabled(monkeypatch) -> None:
    monkeypatch.setenv("APPS_RG_ENABLE_R1B_SEMANTIC_CACHE", "0")
    assert emb.semantic_cache_r1b_eligible(_settings(semantic_enabled=True)) is False


def test_opt_in_with_embeddings_unavailable_is_disabled(monkeypatch) -> None:
    monkeypatch.setenv("APPS_RG_ENABLE_R1B_SEMANTIC_CACHE", "1")
    assert emb.semantic_cache_r1b_eligible(_settings(semantic_enabled=False, model_resolved=False)) is False


def test_opt_in_with_embeddings_eligible_is_enabled(monkeypatch) -> None:
    monkeypatch.setenv("APPS_RG_ENABLE_R1B_SEMANTIC_CACHE", "1")
    assert emb.semantic_cache_r1b_eligible(_settings(semantic_enabled=True)) is True


def test_normal_generation_required_when_r1b_disabled(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.delenv("APPS_RG_ENABLE_R1B_SEMANTIC_CACHE", raising=False)
    monkeypatch.setattr(preflight_mod, "check_r1a_cache", lambda *_args, **_kwargs: None)

    def _no_r1b(*_args, **_kwargs):
        raise AssertionError("R1B preflight must not run without explicit opt-in")

    monkeypatch.setattr(preflight_mod, "execute_whole_run_r1b_preflight", _no_r1b)
    outcome = preflight_mod.run_whole_run_cache_preflight(
        entrypoint=preflight_mod.ENTRYPOINT_CANONICAL_DISPATCH,
        raw_request={"resume_hash": "r", "jd_hash": "j"},
        target_company="Co",
        target_role="Role",
        artifact_dir=tmp_path / "run",
        runs_dir=tmp_path,
    )
    assert outcome.generation_required is True
    assert outcome.r1b_result is None


def test_bootstrap_does_not_enable_r1b_but_preserves_graph_c0_env(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.delenv("SEMANTIC_CACHE_D2_ENABLED", raising=False)
    monkeypatch.delenv("APPS_RG_ENABLE_R1B_SEMANTIC_CACHE", raising=False)
    monkeypatch.setattr(
        emb,
        "_resolve_local_bge_path",
        lambda _model_id: (str(tmp_path), True, "local"),
    )
    applied = emb.bootstrap_apps_rg_embedding_env(repo_root=tmp_path)
    assert "SEMANTIC_CACHE_D2_ENABLED" not in applied
    assert "APPS_RG_ENABLE_R1B_SEMANTIC_CACHE" not in applied
    assert "APPS_RG_ENABLE_R1B_SEMANTIC_CACHE" not in os.environ
    assert emb.semantic_cache_r1b_eligible(_settings(semantic_enabled=True)) is False
    assert applied["APPS_RG_C03_GRAPH_MANDATORY"] == "1"
