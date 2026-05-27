"""W9 contract: graph-skills operator guide on disk with canonical CLI law."""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
GUIDE = REPO / "docs" / "apps_rg" / "graph_skills_quality_operator_guide.md"


def test_operator_guide_canonical_lane_and_whole_run_cli() -> None:
    text = GUIDE.read_text(encoding="utf-8")
    required = (
        "python -m apps_rg --section",
        "Canonical whole-resume CLI",
        "python -m apps_rg \\",
        "Brown & Brown",
        "brown_brown_svp_it_strategy_innovation_briefing.md",
        "executive_summary",
        "competencies",
        "Forbidden as product proof",
        "broad_skills_ledger",
        "emit_graph_skills_quality_w9.py",
        "graph_skills_utilization_receipt.json",
        "3701dd5b1d6e0c92db394d6bf1879574e4ad638094d9b453f6d35e264e8e573f",
    )
    missing = [needle for needle in required if needle not in text]
    assert not missing, f"operator guide missing W9 sections: {missing}"
