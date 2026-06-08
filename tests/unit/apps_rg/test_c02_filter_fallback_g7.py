"""W2 / G7: a section metadata filter must not silently discard 100% of candidates.

Plan: apps-rg-e2e-gap-remediation-7e2d9c.

When the narrow section filter (app + source_class + JD metadata) matches nothing on a populated
collection, _perform_bounded_section_retrieval re-queries ONCE with the broad app+source_class
clause; if that matches, the JD/section metadata filter removed all candidates — the lane falls
back to the broader group and the section trace names the cause (filter_removed_all +
applied_where_filter G7 marker) rather than reporting a falsely empty section.

Pure product-mode unit test: fakes the profile + embedding so only the fallback logic is exercised.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from apps_rg.runtime.bindings import c0_binding


class _FakeProfile:
    enabled = True
    collection_name = "fact_vectors"
    max_total_items = 10
    max_sections = 5

    def get_sections(self):
        return [
            {"section_id": "competencies", "source_class_allowlist": ["candidate_profile"], "dense_top_k": 3}
        ]

    def resolve_section_id(self, section_id):
        return section_id

    def build_query_for_section(self, section, app_payload):
        return "competencies query"

    def section_sparse_config(self, section):
        return {}

    def any_sparse_enabled(self):
        return False


class _FakeMetaProfile:
    def build_chroma_where_clause(self, app_payload, *, source_class_allowlist):
        # Narrow clause: differs from the broad app+source_class clause by a JD metadata filter.
        return {
            "$and": [
                {"app": "apps_rg"},
                {"source_class": {"$in": list(source_class_allowlist)}},
                {"target_company": "Acme"},
            ]
        }


class _TwoCallCollection:
    """Narrow query (1st call) returns nothing; broad query (2nd call) returns one item."""

    def __init__(self):
        self.calls = []

    def query(self, *, query_embeddings, n_results, where):
        self.calls.append(where)
        if len(self.calls) == 1:
            return {"ids": [[]], "metadatas": [[]], "documents": [[]], "distances": [[]]}
        return {
            "ids": [["doc1"]],
            "metadatas": [[{
                "source_class": "candidate_profile",
                "citation_anchor": "anchor1",
                "chunk_digest": "digest1",
                "source_document_id": "src1",
            }]],
            "documents": [["broad fallback evidence text"]],
            "distances": [[0.2]],
        }


@pytest.fixture
def _isolated(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(c0_binding, "SectionRetrievalProfile", _FakeProfile)
    monkeypatch.setattr(c0_binding, "MetadataFilterProfile", _FakeMetaProfile)
    monkeypatch.setattr(c0_binding, "_get_embedding_model", lambda: object())
    monkeypatch.setattr(c0_binding, "_run_section_sparse_lane", lambda *a, **k: None)
    monkeypatch.setattr(
        "tools.ingestion.chroma_ingest_pipeline.embed_text",
        lambda model, text: [0.1] * 1024,
    )
    monkeypatch.setattr(
        "apps_rg.runtime.embedding_settings.resolve_apps_rg_embedding_settings",
        lambda **kwargs: SimpleNamespace(embedding_model_name="BAAI/bge-m3"),
    )
    monkeypatch.setattr(
        "apps_rg.runtime.embedding_settings.assert_dense_retrieval_allowed",
        lambda settings: None,
    )


def test_section_filter_removed_all_falls_back_and_names_reason(_isolated) -> None:
    collection = _TwoCallCollection()
    items, _verdicts, status, _sparse, _scores, traces = c0_binding._perform_bounded_section_retrieval(
        "",
        {"jd_payload": {"target_company": "Acme"}},
        "digest",
        "2026-06-08T00:00:00Z",
        chroma_collection=collection,
        section_id_filter="competencies",
    )

    # Bounded fallback fired: exactly two queries (narrow then broad).
    assert len(collection.calls) == 2
    # The lane now yields evidence rather than a falsely empty section.
    assert status == "PASS"
    assert len(items) == 1
    # The trace names the cause.
    assert len(traces) == 1
    assert traces[0].filter_removed_all is True
    assert "G7_fallback_from_section_filter" in traces[0].applied_where_filter
    assert traces[0].raw_dense_hit_count == 1


def test_no_fallback_when_narrow_filter_yields_hits(_isolated, monkeypatch) -> None:
    """If the narrow filter already matches, no broad re-query and filter_removed_all stays False."""

    class _OneHitCollection:
        def __init__(self):
            self.calls = []

        def query(self, *, query_embeddings, n_results, where):
            self.calls.append(where)
            return {
                "ids": [["doc1"]],
                "metadatas": [[{"source_class": "candidate_profile", "citation_anchor": "a", "chunk_digest": "d"}]],
                "documents": [["narrow hit"]],
                "distances": [[0.1]],
            }

    collection = _OneHitCollection()
    items, _v, status, _s, _sc, traces = c0_binding._perform_bounded_section_retrieval(
        "",
        {"jd_payload": {"target_company": "Acme"}},
        "digest",
        "2026-06-08T00:00:00Z",
        chroma_collection=collection,
        section_id_filter="competencies",
    )
    assert len(collection.calls) == 1  # no broad re-query
    assert status == "PASS"
    assert len(items) == 1
    assert traces[0].filter_removed_all is False
