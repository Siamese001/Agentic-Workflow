from __future__ import annotations

import sys
from types import SimpleNamespace

import pytest

from apps_rg.runtime.bindings.c0_binding import C0EvidenceGapError
from apps_rg.runtime.c0 import c02_product_hybrid_retrieval as product_hybrid


def test_product_hybrid_missing_fact_vectors_collection_is_evidence_gap(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    monkeypatch.setattr(
        product_hybrid,
        "product_hybrid_retrieval_required",
        lambda section_id: True,
    )
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(tmp_path))
    monkeypatch.setitem(
        sys.modules,
        "chromadb",
        SimpleNamespace(PersistentClient=lambda path: object()),
    )

    from apps_rg.runtime import chroma_precomputed_collection
    from apps_rg.runtime import embedding_settings

    monkeypatch.setattr(
        embedding_settings,
        "apply_apps_rg_embedding_env_guards",
        lambda **kwargs: None,
    )
    monkeypatch.setattr(
        embedding_settings,
        "resolve_apps_rg_embedding_settings",
        lambda **kwargs: SimpleNamespace(route_result="PASS", decisive_reason=""),
    )
    monkeypatch.setattr(
        chroma_precomputed_collection,
        "get_precomputed_embeddings_collection_for_query",
        lambda client, name: (_ for _ in ()).throw(RuntimeError("Collection [fact_vectors] does not exist")),
    )

    with pytest.raises(C0EvidenceGapError, match="fact_vectors collection is unavailable"):
        product_hybrid.perform_product_hybrid_retrieval(
            section_id="unify_bullets",
            app_payload={"jd_text": "regulated insurance transformation"},
            evidence_digest="abc123",
            timestamp_iso="2026-06-07T00:00:00+00:00",
        )
