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

    out = render(run_dir)

    assert "## BCG Competencies Improvement Report" in out
    assert "partnership-ordered" in out
    assert "selector rejected `32`" in out
    assert "Strategic Partnerships & Ecosystem Execution" in out
    assert "competencies_visible_graph_surface_enrichment_receipt_v1" in out
