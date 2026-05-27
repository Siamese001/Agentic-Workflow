"""Contract tests: apps_rg C0.1–C0.7 subphase bindings to agentic_core (no LLM)."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from agentic_core.knowledge.retrieval import merge_dense_sparse_rrf
from agentic_core.runtime.contracts.final_evidence_contract import (
    ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
    FinalEvidenceContract,
    SUPPORT_STATUS_EMPTY,
    SUPPORT_STATUS_PASS,
    SUPPORT_STATUS_WEAK,
)
from agentic_core.runtime.contracts.route_contract import GraphTraversePolicy
from apps_rg.runtime.bindings.c0_binding import (
    C0_GRAPH_LANE_NA_REF,
    C0_METADATA_FILTER_REF,
    C0_QUERY_VEC_REF_BGE,
    _compute_support_status,
    _resolve_spine_graph_expansion_refs,
)
from apps_rg.runtime.bindings.l1_binding import L1PlanContract, _resume_evidence_grounding_required
from apps_rg.runtime.spine.c0_fec_compose import emit_spine_c0_fec_artifacts
from apps_rg.runtime.spine.section_c0_retrieve import (
    STOP_AS_EVIDENCE_GAP,
    StopAsEvidenceGapError,
    apply_spine_c03_overlay_to_bridge_doc,
    assert_no_stop_as_evidence_gap,
)

REPO = Path(__file__).resolve().parents[2]


class TestC01L1GroundingBinding:
    def test_l1_plan_contract_importable(self) -> None:
        assert L1PlanContract is not None

    def test_resume_generation_grounding_required(self) -> None:
        assert _resume_evidence_grounding_required("generate_scratch") is True


class TestC02DenseRetrievalBinding:
    def test_bounded_section_retrieval_symbol_exists(self) -> None:
        from apps_rg.runtime.bindings import c0_binding as mod

        assert callable(getattr(mod, "_perform_bounded_section_retrieval", None))

    def test_c0_dense_ref_constants(self) -> None:
        assert "bge-m3" in C0_QUERY_VEC_REF_BGE
        assert "chroma_where" in C0_METADATA_FILTER_REF


class TestC03GraphRagBinding:
    def test_resolve_spine_graph_na_when_policy_inactive(self) -> None:
        route = SimpleNamespace(
            graph_traverse_policy=GraphTraversePolicy(
                graph_expansion_allowed=True,
                max_hops=1,
                live_wiring_deferred=True,
            )
        )
        refs = _resolve_spine_graph_expansion_refs(route, [])
        assert refs == (C0_GRAPH_LANE_NA_REF,)

    def test_maybe_run_graph_rag_import_from_agentic_core(self) -> None:
        from agentic_core.runtime.c0.c0_3_graph_rag_executor import maybe_run_graph_rag

        assert callable(maybe_run_graph_rag)


class TestC04RrfMergeBinding:
    def test_merge_dense_sparse_rrf_is_agentic_core_symbol(self) -> None:
        assert merge_dense_sparse_rrf.__module__.startswith("agentic_core")

    def test_rrf_dedupe_deterministic(self) -> None:
        from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import (
            HybridSearchResult,
        )

        dense = [HybridSearchResult(chunk_id="a", content="a", combined_score=1.0)]
        sparse = [
            HybridSearchResult(chunk_id="a", content="a", combined_score=0.5),
            HybridSearchResult(chunk_id="b", content="b", combined_score=0.3),
        ]
        merged = merge_dense_sparse_rrf(dense, sparse)
        ids = [m.chunk_id for m in merged]
        assert ids[0] == "a"
        assert "b" in ids


class TestC05FecBinding:
    def test_final_evidence_contract_prompt_slot(self) -> None:
        fec = FinalEvidenceContract(
            request_id="r",
            run_id="run",
            app_id="apps_rg",
            trace_id="t",
            l5_certification_ref="test:valid:w6",
            support_status=SUPPORT_STATUS_PASS,
            support_target_met=True,
            final_evidence_digest="d",
        )
        assert fec.support_status in (SUPPORT_STATUS_PASS, SUPPORT_STATUS_WEAK, SUPPORT_STATUS_EMPTY)
        assert ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY


class TestC06SupportStatusGap:
    def test_compute_support_status_empty(self) -> None:
        assert _compute_support_status([]) == SUPPORT_STATUS_EMPTY

    def test_stop_as_evidence_gap_on_weak(self) -> None:
        fec = FinalEvidenceContract(
            request_id="r",
            run_id="run",
            app_id="apps_rg",
            trace_id="t",
            l5_certification_ref="test:valid:w6",
            support_status=SUPPORT_STATUS_WEAK,
            support_target_met=False,
        )
        with pytest.raises(StopAsEvidenceGapError, match=STOP_AS_EVIDENCE_GAP):
            assert_no_stop_as_evidence_gap(
                grounding_required=True,
                fec=fec,
                section_id="executive_summary",
            )


class TestC07RetrievalQualitySpan:
    def test_emit_spine_c0_fec_artifacts_emits_c0_graph_lane_receipt(
        self,
        tmp_path: Path,
    ) -> None:
        from apps_rg.runtime.spine.c0_fec_compose import SectionFecBridge

        bridge = SectionFecBridge(
            section_id="executive_summary",
            bridge_doc={
                "section_id": "executive_summary",
                "route_contract_ref": "route_contract.json",
                "source_fact_ids": ["fact_1"],
                "graph_expansion_refs": ["ref:graph:node:skill_1"],
                "spine_c0_retrieve_receipt": {
                    "canonical_c0_3_graph_claimed": True,
                    "graph_expansion_refs": ["ref:graph:node:skill_1"],
                },
            },
        )
        paths = emit_spine_c0_fec_artifacts(tmp_path, bridge)
        assert (tmp_path / "c0_graph_lane_receipt.json").is_file()
        assert "final_evidence_contract" in paths

    def test_c0_fec_compose_wires_spine_span_emit(self) -> None:
        import inspect

        from apps_rg.runtime.spine import c0_fec_compose as mod

        src = inspect.getsource(mod.wire_spine_c0_fec_for_section)
        assert "emit_spine_span_event" in src
        assert 'layer_key="C0"' in src or "layer_key='C0'" in src


class TestSpineC03OverlayPreservesEvidenceRoom:
    def test_overlay_sets_core_c03_without_changing_producer(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from apps_rg.runtime.spine.section_c0_retrieve import (
            SectionSpineC0RetrieveResult,
            invoke_section_spine_c0_retrieve,
        )
        from apps_rg.runtime.spine.front_contracts import (
            build_section_front_spine_from_args,
            deactivate_fixture_dev_bypass,
        )

        deactivate_fixture_dev_bypass()
        spine = build_section_front_spine_from_args(
            section_id="executive_summary",
            args=SimpleNamespace(
                target_company="Acme",
                target_title="VP",
                target_role="VP",
                jd_text="JD",
                briefing="brief",
                base_resume_ref="",
            ),
            repo_root=REPO,
        )
        live_fec = FinalEvidenceContract(
            request_id="r",
            run_id="run",
            app_id="apps_rg",
            trace_id="t",
            l5_certification_ref="test:valid:w6",
            support_status=SUPPORT_STATUS_PASS,
            support_target_met=True,
            final_evidence_digest="d",
            graph_expansion_refs=("ref:graph:node:n1",),
        )
        monkeypatch.setattr(
            "apps_rg.runtime.spine.section_c0_retrieve.c0_retrieve_apps_rg",
            lambda **_: live_fec,
        )
        result = invoke_section_spine_c0_retrieve(
            front_spine=spine,
            section_id="executive_summary",
        )
        merged = apply_spine_c03_overlay_to_bridge_doc(
            {
                "producer_stage": "section_c0_evidence_room",
                "canonical_c0_3_claimed": False,
            },
            spine=result,
        )
        assert merged["producer_stage"] == "section_c0_evidence_room"
        assert merged["canonical_c0_3_claimed"] is True
        assert merged["core_c03_graph_rag_used"] is True
