"""Runtime graph-skills artifact persistence (D6 hardening)."""
from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.graph_selection_rationale import SCHEMA as RATIONALE_SCHEMA
from apps_rg.runtime.graph_skills_run_artifacts import (
    RATIONALE_FILENAME,
    persist_graph_skills_lane_artifacts,
)

REPO = Path(__file__).resolve().parents[3]


def test_persist_graph_selection_rationale_to_run_dir(tmp_path: Path) -> None:
    jd_path = REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt"
    brief_path = REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md"
    payload = {
        "target_company": "Brown & Brown",
        "target_title": "SVP IT Strategy & Innovation",
        "jd_text": jd_path.read_text(encoding="utf-8"),
        "briefing": brief_path.read_text(encoding="utf-8"),
        "proof_pool_metadata": {},
    }
    out = persist_graph_skills_lane_artifacts(
        tmp_path,
        section_id="executive_summary",
        runtime_payload=payload,
        repo_root=REPO,
    )
    assert out[RATIONALE_FILENAME]
    rationale = json.loads((tmp_path / RATIONALE_FILENAME).read_text(encoding="utf-8"))
    assert rationale["schema"] == RATIONALE_SCHEMA
    assert rationale["jd_subgraph_policy"]["jd_used_as_proof"] is False
    assert rationale["evidence_authority"] == "augmented_skills_graph"


def test_persist_skips_unknown_section(tmp_path: Path) -> None:
    out = persist_graph_skills_lane_artifacts(
        tmp_path,
        section_id="not_a_lane",
        runtime_payload={"jd_text": "x", "target_company": "c", "target_role": "r"},
    )
    assert out[RATIONALE_FILENAME] is None
