"""Tests for the report-only graph-skill utilization tool (H3)."""
from __future__ import annotations

import json
from pathlib import Path

from tools.apps_rg.graph_skill_utilization_report import build_report, render_markdown


def _write(path: Path, blob: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(blob), encoding="utf-8")


def _make_run(tmp: Path) -> Path:
    run = tmp / "modular_r4"
    # spine final_resume.json — competencies with one D8-usable skill + per-lane plans
    spine = {
        "sections": [
            {
                "section_id": "competencies",
                "l2_output_snapshot": {
                    "competencies": [
                        {"category_label": "AI", "terms": [{"text": "governed agentic platform delivery"}]}
                    ],
                    "claim_ledger": [{"source_fact_ids": ["fact_p1"]}],
                    "selected_fact_plan": {"facts": [{"skill_id": "skill_alpha"}, {"skill_id": "skill_beta"}]},
                },
            },
            {
                "section_id": "unify_bullets",
                "l2_output_snapshot": {"selected_fact_plan": {"facts": [{"skill_id": "skill_gamma"}]}},
            },
            {
                "section_id": "ibm_bullets",
                "l2_output_snapshot": {"selected_fact_plan": {"facts": [{"fact_id": "fact_x"}]}},
            },
        ]
    }
    _write(run / "final_resume_assembly" / "final_resume.json", spine)
    # competencies runtime_payload with proof-pool bundles (the scorer's skill rows)
    rp = {
        "allowed_fact_ids": ["fact_p1"],
        "proof_pool_metadata": {
            "competency_capability_bundles": [
                {
                    "linked_source_fact_ids": ["fact_p1"],
                    "bound_skills": [
                        {"skill_id": "skill_alpha", "allowed_phrases": ["governed agentic platform"]},
                        {"skill_id": "skill_beta", "allowed_phrases": ["unused phrase nowhere"]},
                    ],
                }
            ]
        },
    }
    _write(run / "sections" / "competencies" / "real" / "competencies_x" / "runtime_payload.json", rp)
    return run


def test_build_report_competencies_d8_and_per_lane(tmp_path: Path) -> None:
    run = _make_run(tmp_path)
    report = build_report(run)

    assert report["report_class"] == "REPORT_ONLY_NON_BLOCKING"
    comp = report["competencies_d8_utilization"]
    assert comp["available"] is True
    assert comp["eligible_skill_count"] == 2
    # skill_alpha's phrase appears in the display text AND fact_p1 is cited -> D8-used.
    # skill_beta's phrase is absent -> not used.
    assert comp["used_skill_count"] == 1
    assert "skill_alpha" in comp["used_skill_ids"]
    assert "skill_beta" not in comp["used_skill_ids"]

    by_lane = {r["section_id"]: r for r in report["per_lane_selection_plan_skill_refs"]}
    assert by_lane["competencies"]["selection_plan_skill_ref_count"] == 2
    assert by_lane["unify_bullets"]["selection_plan_skill_ref_count"] == 1
    assert by_lane["ibm_bullets"]["selection_plan_skill_ref_count"] == 0


def test_render_markdown_smoke(tmp_path: Path) -> None:
    report = build_report(_make_run(tmp_path))
    md = render_markdown(report)
    assert "Graph-Skill Utilization" in md
    assert "D8 genuine utilization" in md
    assert "skill_alpha" in md
