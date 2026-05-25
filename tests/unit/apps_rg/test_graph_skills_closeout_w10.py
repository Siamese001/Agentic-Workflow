"""W10 contract: closeout JSON schema and honest non-claims."""
from __future__ import annotations

import json
from pathlib import Path

from apps_rg.fact_inventory.graph_skills_quality_enhancement_closeout import (
    PLAN_ID,
    SCHEMA,
    build_closeout,
)

REPO = Path(__file__).resolve().parents[3]
CLOSEOUT = REPO / "docs" / "reports" / "apps_rg" / "graph_skills_quality_enhancement_closeout.json"


def test_closeout_builder_schema() -> None:
    doc = build_closeout(REPO, git_commit="test")
    assert doc["schema"] == SCHEMA
    assert doc["plan_id"] == PLAN_ID
    assert doc["claims_release_eligible"] is False
    assert doc["claims_dynamic_graphrag_traverse"] is False
    assert doc["claims_c03_unified_pipeline_bound"] is False
    matrix = doc["proof_classification_matrix"]
    dod_ids = {row["dod_id"] for row in matrix}
    assert dod_ids >= {f"D{i}" for i in range(1, 17)}
    d6 = doc["d6_lane_matrix"]
    assert len(d6) == 7
    for row in d6:
        assert "x3_code_raw" in row
        assert "x3_normalized" in row
        assert "live_x3_allow_claimed" in row
    d16 = next(r for r in matrix if r["dod_id"] == "D16")
    assert d16["status"] == "BLOCKED"
    assert d16["primary_proof_class"] == "REAL_LLM_RUNTIME_PROOF"


def test_closeout_on_disk_after_emit() -> None:
    if not CLOSEOUT.is_file():
        doc = build_closeout(REPO)
        CLOSEOUT.parent.mkdir(parents=True, exist_ok=True)
        CLOSEOUT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    doc = json.loads(CLOSEOUT.read_text(encoding="utf-8"))
    assert doc["wave_receipt_paths"]
    assert any(
        p.endswith("graph_skills_quality_w10_ag_receipt.json") for p in doc["wave_receipt_paths"]
    )
    assert doc["brown_fixture_digests"]["pass"] is True
