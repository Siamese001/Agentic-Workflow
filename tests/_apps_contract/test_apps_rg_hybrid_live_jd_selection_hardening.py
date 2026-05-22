"""H5 contract tests — hybrid live JD selection plan (W0b)."""

from __future__ import annotations

from dataclasses import replace
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.runtime.contracts.final_evidence_contract import EvidenceItem
from apps_rg.runtime.c0.c02_hybrid_receipt_truth import FORBIDDEN_RECEIPT_REASON
from apps_rg.runtime.c0.c02_product_hybrid_retrieval import (
    perform_product_hybrid_retrieval,
    product_hybrid_retrieval_required,
)
from apps_rg.runtime.c0.hybrid_informed_fact_plan_reorder import (
    apply_hybrid_informed_fact_plan_reorder,
    reorder_selected_fact_plan_by_hybrid_scores,
)
from apps_rg.runtime.c02_chroma_lifecycle import build_c02_chroma_query_receipt


def _sample_plan() -> dict:
    return {
        "section_id": "executive_summary",
        "selection_method": "augmented_skills_graph_c03_graphrag",
        "facts": [
            {"fact_id": "fact_low", "text": "low score fact"},
            {"fact_id": "fact_high", "text": "high score fact"},
            {"fact_id": "fact_mid", "text": "mid score fact"},
        ],
        "required_fact_ids": ["fact_low", "fact_high", "fact_mid"],
    }


class TestHybridRequiredPolicy:
    def test_required_on_product_fail_closed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
        monkeypatch.delenv("APPS_RG_ALLOW_PRODUCT_SHORTCUTS", raising=False)
        assert product_hybrid_retrieval_required("executive_summary") is True

    def test_not_required_under_test_harness(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("APPS_RG_TEST_HARNESS", "1")
        assert product_hybrid_retrieval_required("executive_summary") is False


class TestSparseBlocksFailClosed:
    def test_missing_chroma_dir_raises_gap(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from apps_rg.runtime.bindings.c0_binding import C0EvidenceGapError

        monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
        monkeypatch.delenv("APPS_RG_ALLOW_PRODUCT_SHORTCUTS", raising=False)
        monkeypatch.delenv("CHROMA_PERSIST_DIR", raising=False)
        with pytest.raises(C0EvidenceGapError, match="CHROMA_PERSIST_DIR"):
            perform_product_hybrid_retrieval(
                section_id="executive_summary",
                app_payload={"jd_text": "Brown and Brown SVP IT Strategy"},
                evidence_digest="abc",
                timestamp_iso="2026-05-22T00:00:00Z",
            )

    def test_sparse_unavailable_raises_on_mandatory_lane(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from apps_rg.runtime.bindings.c0_binding import C0EvidenceGapError

        monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
        monkeypatch.delenv("APPS_RG_ALLOW_PRODUCT_SHORTCUTS", raising=False)
        monkeypatch.setenv("CHROMA_PERSIST_DIR", "/tmp/chroma_test")
        hit = EvidenceItem(
            source="chromadb:fact_vectors:doc1",
            content="retrieved",
            source_id="doc1",
        )
        sparse_unavail = ["ref:sparse:lane:apps_rg.executive_summary.sparse:status=UNAVAILABLE:hits=0"]

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
                return_value=([hit], [], "PASS", sparse_unavail, [], []),
            ),
        ):
            mock_emb.return_value = MagicMock(route_result="PASS")
            with pytest.raises(C0EvidenceGapError, match="BM25 unavailable"):
                perform_product_hybrid_retrieval(
                    section_id="executive_summary",
                    app_payload={"jd_text": "Brown and Brown SVP IT Strategy innovation"},
                    evidence_digest="digest",
                    timestamp_iso="2026-05-22T00:00:00Z",
                    chromadb_path="/tmp/chroma_test",
                )


class TestLedgerOnlyForbiddenWhenHybridRequired:
    def test_hybrid_required_skipped_mode_not_ledger_only(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
        monkeypatch.delenv("APPS_RG_ALLOW_PRODUCT_SHORTCUTS", raising=False)
        receipt = build_c02_chroma_query_receipt(
            section_id="executive_summary",
            c05_receipt={"spine_chroma_enrich": False, "c02_vector_query": {}},
        )
        assert receipt["c0_retrieval_mode"] != "ledger_only"
        assert receipt["reason"] != FORBIDDEN_RECEIPT_REASON
        if receipt["c0_retrieval_mode"] == "C0_RETRIEVAL_LANE_SKIPPED":
            assert receipt.get("product_hybrid_required") is True

    def test_product_hybrid_success_not_ledger_only(self) -> None:
        receipt = build_c02_chroma_query_receipt(
            section_id="executive_summary",
            c05_receipt={
                "c02_vector_query": {
                    "product_hybrid_required": True,
                    "product_hybrid_attempted": True,
                    "attempted": True,
                    "reason": "product_hybrid_bounded_section_retrieval",
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
        assert receipt["reason"] == "product_hybrid_bounded_section_retrieval"


class TestSpineEnvDoesNotGateProductHybrid:
    def test_hybrid_runs_with_spine_env_unset(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("APPS_RG_SPINE_CHROMA_ENRICH", raising=False)
        monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
        monkeypatch.delenv("APPS_RG_ALLOW_PRODUCT_SHORTCUTS", raising=False)
        monkeypatch.setenv("CHROMA_PERSIST_DIR", "/tmp/chroma_test")
        hit = EvidenceItem(
            source="chromadb:fact_vectors:doc1",
            content="retrieved",
            source_id="doc1",
            dense_score=0.9,
            bm25_score=0.8,
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
                app_payload={"jd_text": "Brown and Brown SVP IT Strategy"},
                evidence_digest="digest",
                timestamp_iso="2026-05-22T00:00:00Z",
                chromadb_path="/tmp/chroma_test",
            )
        vq = out["c02_vector_query"]
        assert vq["product_hybrid_attempted"] is True
        assert vq["reason"] != FORBIDDEN_RECEIPT_REASON


class TestW2BReorderLaw:
    def test_reorder_preserves_fact_id_set(self) -> None:
        plan = _sample_plan()
        before = {str(f["fact_id"]) for f in plan["facts"]}
        reordered = reorder_selected_fact_plan_by_hybrid_scores(
            plan,
            score_by_fact_id={"fact_low": 0.1, "fact_mid": 0.5, "fact_high": 0.9},
        )
        after = {str(f["fact_id"]) for f in reordered["facts"]}
        assert before == after
        assert len(reordered["facts"]) == len(plan["facts"])

    def test_reorder_changes_order_by_score(self) -> None:
        plan = _sample_plan()
        reordered = reorder_selected_fact_plan_by_hybrid_scores(
            plan,
            score_by_fact_id={"fact_low": 0.1, "fact_mid": 0.5, "fact_high": 0.9},
        )
        ids = [f["fact_id"] for f in reordered["facts"]]
        assert ids[0] == "fact_high"
        assert ids[-1] == "fact_low"

    def test_reorder_does_not_mutate_authority_fields(self) -> None:
        plan = _sample_plan()
        for f in plan["facts"]:
            f["proof_status"] = "proof_eligible"
            f["authority_class"] = "PRIMARY"
        reordered = reorder_selected_fact_plan_by_hybrid_scores(
            plan,
            score_by_fact_id={"fact_low": 0.1, "fact_high": 0.9, "fact_mid": 0.5},
        )
        for orig, new in zip(
            sorted(plan["facts"], key=lambda x: x["fact_id"]),
            sorted(reordered["facts"], key=lambda x: x["fact_id"]),
        ):
            assert orig["proof_status"] == new["proof_status"]
            assert orig["authority_class"] == new["authority_class"]

    def test_hybrid_score_map_resolves_fact_id_from_citation_anchor(self) -> None:
        from apps_rg.runtime.c0.hybrid_informed_fact_plan_reorder import hybrid_score_map_from_enrichment

        item = EvidenceItem(
            source="chromadb:fact_vectors:chunk1",
            content="Platform scale for fact_engineering_platform_006",
            source_id="chunk1",
            citation_anchor="fv:exec:001",
            dense_score=0.88,
        )
        item = replace(item, citation_anchor="anchor:fact_engineering_platform_006:001")
        scores = hybrid_score_map_from_enrichment(
            [item], allowed_fact_ids={"fact_engineering_platform_006", "fact_low"}
        )
        assert scores.get("fact_engineering_platform_006") == 0.88

    def test_apply_from_hybrid_doc(self) -> None:
        plan = _sample_plan()
        hybrid_doc = {
            "enrichment_items": [
                replace(
                    EvidenceItem(
                        source="chromadb:fact_vectors:fact_high",
                        content="x",
                        source_id="fact_high",
                    ),
                    dense_score=0.95,
                ),
                replace(
                    EvidenceItem(
                        source="chromadb:fact_vectors:fact_low",
                        content="y",
                        source_id="fact_low",
                    ),
                    bm25_score=0.2,
                ),
            ]
        }
        out = apply_hybrid_informed_fact_plan_reorder(plan, hybrid_doc=hybrid_doc)
        assert out["hybrid_informed_reorder"]["applied"] is True
        assert out["facts"][0]["fact_id"] == "fact_high"
