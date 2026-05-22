"""W4.3 — product hybrid retrieval (profile-driven; no spine-enrich env)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from agentic_core.runtime.contracts.final_evidence_contract import EvidenceItem
from apps_rg.runtime.c0.c02_hybrid_receipt_truth import FORBIDDEN_RECEIPT_REASON
from apps_rg.runtime.c0.c02_product_hybrid_retrieval import (
    normalize_section_app_payload,
    perform_product_hybrid_retrieval,
    product_hybrid_retrieval_required,
)
from apps_rg.runtime.c0.c05_fec_packet import build_c05_final_evidence_contract
from apps_rg.runtime.c0.c0_section_authority import AUTHORITY_CLASS_SPINE_ENRICHMENT

REQUIRED_TRUTH_KEYS = frozenset(
    {
        "retrieval_profile_ref",
        "product_hybrid_required",
        "product_hybrid_attempted",
        "dense_attempted",
        "sparse_attempted",
        "bm25_available",
        "failure_reason",
        "proof_classification",
    }
)


class TestProductHybridPolicy:
    def test_not_required_under_test_harness(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("APPS_RG_TEST_HARNESS", "1")
        assert product_hybrid_retrieval_required("executive_summary") is False

    def test_required_on_product_fail_closed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
        monkeypatch.delenv("APPS_RG_ALLOW_PRODUCT_SHORTCUTS", raising=False)
        assert product_hybrid_retrieval_required("executive_summary") is True

    def test_normalize_flat_jd_into_jd_payload(self) -> None:
        payload = normalize_section_app_payload(
            {"jd_text": "Senior VP IT Strategy at Brown and Brown insurance brokerage"}
        )
        assert payload["jd_payload"]["jd_text"].startswith("Senior VP")


class TestC05ProductHybridReceipt:
    def test_hybrid_merges_with_positive_truth_fields(self) -> None:
        hybrid_item = EvidenceItem(
            source="chromadb:fact_vectors:hybrid-1",
            content="hybrid enrichment only",
            source_id="hybrid-1",
            authority_class=AUTHORITY_CLASS_SPINE_ENRICHMENT,
        )
        hybrid_doc = {
            "required": True,
            "enrichment_items": [hybrid_item],
            "c02_vector_query": {
                "product_hybrid_required": True,
                "product_hybrid_attempted": True,
                "dense_attempted": True,
                "sparse_attempted": True,
                "bm25_available": True,
                "failure_reason": "product_hybrid_bounded_section_retrieval",
                "lanes": {"dense": "completed", "sparse": "completed", "metadata": "completed"},
                "c0_retrieval_mode": "ledger_plus_hybrid_retrieval",
            },
        }
        fec, receipt = build_c05_final_evidence_contract(
            section_id="executive_summary",
            atoms=[
                {
                    "fact_id": "fact_a",
                    "text_to_embed": "Ledger proof claim with enough length here.",
                    "source_type": "proof_pool",
                    "proof_status": "proof_eligible",
                }
            ],
            strata={},
            graph_bindings=[],
            front_spine=None,
            allowed_fact_ids=["fact_a"],
            product_hybrid=hybrid_doc,
        )
        assert receipt["product_hybrid_enrichment_item_count"] == 1
        vq = receipt["c02_vector_query"]
        assert REQUIRED_TRUTH_KEYS <= set(vq.keys())
        assert vq["product_hybrid_attempted"] is True
        assert vq["failure_reason"] != FORBIDDEN_RECEIPT_REASON
        assert len(fec.evidence_items) == 2


class TestPerformProductHybridRetrieval:
    def test_fail_closed_without_chroma_dir(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from apps_rg.runtime.bindings.c0_binding import C0EvidenceGapError

        monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
        monkeypatch.delenv("APPS_RG_ALLOW_PRODUCT_SHORTCUTS", raising=False)
        monkeypatch.delenv("CHROMA_PERSIST_DIR", raising=False)
        with pytest.raises(C0EvidenceGapError, match="CHROMA_PERSIST_DIR"):
            perform_product_hybrid_retrieval(
                section_id="executive_summary",
                app_payload={"jd_text": "x" * 40},
                evidence_digest="abc",
                timestamp_iso="2026-05-22T00:00:00Z",
            )

    def test_mock_bounded_retrieval_emits_hybrid_receipt(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
        monkeypatch.delenv("APPS_RG_ALLOW_PRODUCT_SHORTCUTS", raising=False)
        monkeypatch.setenv("CHROMA_PERSIST_DIR", "/tmp/chroma_test")
        hit = EvidenceItem(
            source="chromadb:fact_vectors:doc1",
            content="retrieved fact",
            source_id="doc1",
            retrieval_method="dense,sparse",
        )

        with (
            patch(
                "apps_rg.runtime.embedding_settings.apply_apps_rg_embedding_env_guards"
            ),
            patch(
                "apps_rg.runtime.embedding_settings.resolve_apps_rg_embedding_settings"
            ) as mock_emb,
            patch("chromadb.PersistentClient"),
            patch(
                "apps_rg.runtime.chroma_precomputed_collection.get_precomputed_embeddings_collection_for_query"
            ),
            patch(
                "apps_rg.runtime.bindings.c0_binding._perform_bounded_section_retrieval",
                return_value=([hit], [], "PASS", ["ref:sparse:lane:ok"], [], []),
            ),
        ):
            mock_emb.return_value = MagicMock(route_result="PASS")
            out = perform_product_hybrid_retrieval(
                section_id="executive_summary",
                app_payload={"jd_text": "Brown and Brown SVP IT Strategy innovation"},
                evidence_digest="digest",
                timestamp_iso="2026-05-22T00:00:00Z",
                chromadb_path="/tmp/chroma_test",
            )
        assert out["required"] is True
        vq = out["c02_vector_query"]
        assert REQUIRED_TRUTH_KEYS <= set(vq.keys())
        assert vq["product_hybrid_attempted"] is True
        assert vq["failure_reason"] != FORBIDDEN_RECEIPT_REASON


class TestChromaQueryReceipt:
    def test_product_hybrid_receipt_not_ledger_only(self) -> None:
        from apps_rg.runtime.c02_chroma_lifecycle import build_c02_chroma_query_receipt

        receipt = build_c02_chroma_query_receipt(
            section_id="executive_summary",
            c05_receipt={
                "c02_vector_query": {
                    "product_hybrid_required": True,
                    "product_hybrid_attempted": True,
                    "dense_attempted": True,
                    "sparse_attempted": True,
                    "bm25_available": True,
                    "failure_reason": "product_hybrid_bounded_section_retrieval",
                    "lanes": {
                        "dense": "completed",
                        "sparse": "completed",
                        "metadata": "completed",
                    },
                    "c0_retrieval_mode": "ledger_plus_hybrid_retrieval",
                },
            },
        )
        assert receipt["c0_retrieval_mode"] == "ledger_plus_hybrid_retrieval"
        assert receipt["product_hybrid_attempted"] is True
        assert receipt["failure_reason"] != FORBIDDEN_RECEIPT_REASON
