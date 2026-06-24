from __future__ import annotations

import json
from pathlib import Path

from tools.apps_rg.render_run_summary import render


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def test_render_run_summary_surfaces_bcg_competencies_report(tmp_path: Path) -> None:
    run_dir = tmp_path / "anthropic_competencies"
    run_dir.mkdir()
    (run_dir / "competencies_display.txt").write_text(
        "Strategic Partnerships & Ecosystem Execution: hyperscaler alliance co-sell, "
        "cloud partner ecosystem GTM, joint revenue execution\n"
        "Governed Agentic AI Platform Architecture: governed agentic systems architecture, "
        "multi-agent orchestration fabric, agentic control plane\n",
        encoding="utf-8",
    )
    _write_json(
        run_dir / "x3_disposition.json",
        {
            "x3_code": "X3_ALLOW",
            "runtime_generation_status": "REAL_LLM",
            "proof_eligible": True,
        },
    )
    _write_json(
        run_dir / "x2_gate_outputs.json",
        {
            "gates": [
                {"gate_id": "x2_competencies_graph_traversal_sufficiency", "pass": True},
                {"gate_id": "x2_competencies_graph_granularity_gates", "pass": True},
                {"gate_id": "x2_competencies_source_fact_concentration_limit", "pass": True},
                {"gate_id": "x2_competencies_per_category_confidence_nonconstant", "pass": True},
            ]
        },
    )
    _write_json(
        run_dir / "runtime_graph_sourcing_assessment.json",
        {
            "traversal": {
                "target_role_profile": "ai_partnerships_gtm",
                "selection_method": "selected_graph_evidence_plan_competencies",
                "graph_evidence_depth_status": "judge_grade",
                "frontier_size_by_hop_depth": {
                    "0_role_episode_roots": 35,
                    "1_leaf_skill_candidates": 46,
                    "2_metric_outcome_candidates": 29,
                },
                "selected_role_episode_root_count": 8,
                "selected_unique_leaf_skill_count": 26,
                "selected_unique_metric_count": 16,
                "rejected_sibling_skill_count": 21,
                "rejected_sibling_metric_count": 16,
                "selected_vs_rejected_candidate_comparison": {
                    "selector_rejected_neighbor_count": 32,
                },
                "role_specific_axis_coverage": {
                    "covered_axes": ["partner_motions", "co_sell"],
                    "missing_axes": [],
                },
                "graph_evidence_depth_comparison": {
                    "summary": "7/8 rich items -> 8/8 rich items",
                },
            },
            "confidence_decomposition": {
                "category_confidence_values": [0.8277, 0.7213],
            },
        },
    )
    _write_json(
        run_dir / "competencies_visible_graph_surface_enrichment_receipt.json",
        {
            "schema_version": "competencies_visible_graph_surface_enrichment_receipt_v1",
            "rows": [
                {
                    "surface": "competencies",
                    "order_index": 0,
                    "resume_display_label": "Strategic Partnerships & Ecosystem Execution",
                    "competency_bundle_id": "ccb_partnerships_ecosystem_execution",
                    "visible_terms": [
                        "hyperscaler alliance co-sell",
                        "cloud partner ecosystem GTM",
                        "joint revenue execution",
                    ],
                }
            ],
        },
    )
    _write_json(
        run_dir / "c0_evidence_room_receipt.json",
        {
            "c02": {
                "c02_chroma_write": {
                    "attempted": False,
                    "status": "SKIPPED",
                    "upserted_count": 0,
                    "reason": "product_section_skip_lane_upsert",
                },
                "fact_vectors_ingest": {
                    "attempted": False,
                    "status": "SKIPPED",
                    "upserted_count": 0,
                    "reason": "product_section_skip_lane_upsert",
                },
                "fact_vector_index_preflight": {
                    "status": "PASS",
                    "same_run_write_policy": "forbidden_for_product_retrieval",
                    "expected_embedding_model": "BAAI/bge-m3",
                    "expected_embedding_dim": 1024,
                    "chroma_path": "data/cache/chromadb",
                    "manifest_upserted_count": 45,
                    "manifest_collection_count_after": 60,
                    "manifest_sparse_sidecar_built": True,
                    "collection": {
                        "collection_name": "fact_vectors",
                        "collection_count": 60,
                        "section_target_count": 26,
                    },
                },
            },
            "c05": {},
        },
    )
    _write_json(
        run_dir / "c02_vector_query.json",
        {
            "schema_version": "c02_vector_query_v1",
            "section_id": "competencies",
            "product_hybrid_required": True,
            "product_hybrid_attempted": True,
            "lanes": {"dense": "completed", "sparse": "completed", "metadata": "completed"},
            "c0_retrieval_mode": "ledger_plus_hybrid_retrieval",
            "hybrid_enrichment_item_count": 7,
            "status": "PASS",
        },
    )
    _write_json(
        run_dir / "c02_semantic_cache_payload.json",
        {
            "intent_digest": "4d89c23f1d2e1ad35b251d8fd9de0659f6d5c0c6cb91201783530e2da9bd33a9",
            "intent_vector": {
                "embedding_model": "BAAI/bge-m3",
                "dimensions": 1024,
            },
            "query_output_count": 8,
        },
    )

    out = render(run_dir)

    assert "## BCG Competencies Improvement Report" in out
    assert "partnership-ordered" in out
    assert "selector rejected `32`" in out
    assert "Strategic Partnerships & Ecosystem Execution" in out
    assert "competencies_visible_graph_surface_enrichment_receipt_v1" in out
    assert "C0 fact-vector index" in out
    assert "C0.2 retrieval compare" in out
    assert "C0.2 same-run write" in out
    assert "BAAI/bge-m3" in out
    assert "forbidden_for_product_retrieval" in out


def test_render_run_summary_surfaces_bcg_unify_bullets_c0_report(tmp_path: Path) -> None:
    run_dir = tmp_path / "anthropic_unify_bullets"
    run_dir.mkdir()
    (run_dir / "unify_bullets_output.txt").write_text(
        "bul_unify_001: Owned governed multi-agent architecture with deterministic route controls.\n"
        "bul_unify_002: Built partner co-sell motions with cloud alliances and measurable adoption.\n",
        encoding="utf-8",
    )
    _write_json(
        run_dir / "x3_disposition.json",
        {
            "x3_code": "X3_ALLOW",
            "runtime_generation_status": "REAL_LLM",
        },
    )
    _write_json(
        run_dir / "x2_gate_outputs.json",
        {
            "gates": [
                {"gate_id": "x2_unify_each_bullet_approved_metric_outcome_lineage", "pass": True},
                {"gate_id": "x2_unify_each_bullet_metric_outcome_surface_visible", "pass": True},
                {"gate_id": "x2_unify_metric_outcomes_distributed_by_slot", "pass": True},
            ]
        },
    )
    preflight = {
        "section_id": "unify_bullets",
        "status": "PASS",
        "same_run_write_policy": "forbidden_for_product_retrieval",
        "expected_embedding_model": "BAAI/bge-m3",
        "expected_embedding_dim": 1024,
        "chroma_path": "data/cache/chromadb",
        "delayed_loop_policy": {
            "pre_run_fact_vector_index_required": True,
            "live_write_during_c0": False,
            "generated_output_route": "stage_or_semantic_cache_after_generation",
            "promotion_gate": "fact_vectors_staging_to_live_after_validation_or_hitl",
        },
        "collection": {
            "collection_name": "fact_vectors",
            "collection_count": 60,
            "section_target_count": 24,
        },
        "unify_bullets_sufficiency": {
            "status": "PASS",
            "expected_slot_ids": [f"bul_unify_{i:03d}" for i in range(1, 7)],
            "missing_source_fact_slots": [],
            "missing_metric_outcome_slots": [],
            "unique_metric_outcome_ids": [f"metric_{i}" for i in range(1, 7)],
            "metric_distribution_pass": True,
            "graph_traversal_pass": True,
            "graph_granularity_pass": True,
            "graph_traversal_receipt": {
                "selected_role_episode_root_count": 6,
                "selected_unique_leaf_skill_count": 35,
                "selected_unique_metric_count": 21,
            },
        },
    }
    _write_json(
        run_dir / "c0_evidence_room_receipt.json",
        {
            "c02": {
                "c02_chroma_write": {
                    "attempted": False,
                    "status": "SKIPPED",
                    "upserted_count": 0,
                    "reason": "product_section_skip_lane_upsert",
                },
                "fact_vectors_ingest": {
                    "attempted": False,
                    "status": "SKIPPED",
                    "upserted_count": 0,
                    "reason": "product_section_skip_lane_upsert",
                },
                "fact_vector_index_preflight": preflight,
            },
            "c05": {"section_id": "unify_bullets"},
            "c07": {
                "handoff_safe": True,
                "checks": {
                    "unify_bullets_fact_vector_sufficiency_status": "PASS",
                    "unify_bullets_metric_distribution_pass": True,
                },
            },
        },
    )
    _write_json(
        run_dir / "c02_vector_query.json",
        {
            "schema_version": "c02_vector_query_v1",
            "section_id": "unify_bullets",
            "product_hybrid_required": True,
            "product_hybrid_attempted": True,
            "lanes": {"dense": "completed", "sparse": "completed", "metadata": "completed"},
            "c0_retrieval_mode": "ledger_plus_hybrid_retrieval",
            "hybrid_enrichment_item_count": 7,
            "status": "PASS",
        },
    )
    _write_json(
        run_dir / "c02_semantic_cache_payload.json",
        {
            "intent_digest": "4018b73929a5aaaaa",
            "intent_vector": {"embedding_model": "BAAI/bge-m3", "dimensions": 1024},
            "query_output_count": 8,
        },
    )
    out = render(run_dir)

    assert "## BCG Unify Bullets C0-C7 Report" in out
    assert "Unify six-slot sufficiency" in out
    assert "slots `6/6`" in out
    assert "Delayed loop policy" in out
    assert "stage_or_semantic_cache_after_generation" in out
    assert "X2 metric lineage gates" in out
    assert "forbidden_for_product_retrieval" in out
