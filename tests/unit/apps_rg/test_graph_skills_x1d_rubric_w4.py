"""W4: X1D rubric port diff — no masking."""
from __future__ import annotations

from pathlib import Path

from apps_rg.runtime.judges.graph_skills_x1d_rubric_contract import (
    MIN_PASS_THRESHOLD,
    NON_CLAIM_NO_MASKING,
    build_rubric_port_diff,
    collect_current_rubric_snapshots,
)

REPO = Path(__file__).resolve().parents[3]


def test_all_lane_rubrics_meet_w4_markers() -> None:
    snaps = collect_current_rubric_snapshots()
    assert len(snaps) == 7
    for snap in snaps:
        assert snap.default_threshold >= MIN_PASS_THRESHOLD, snap.lane_id
        assert not snap.missing_markers, f"{snap.lane_id} missing {snap.missing_markers}"
        assert not snap.forbidden_markers_found


def test_rubric_port_diff_passes_against_baseline() -> None:
    diff = build_rubric_port_diff(repo_root=REPO)
    assert diff["status"] == "PASS"
    assert diff["any_masking_relaxed"] is False
    assert not diff["invariant_failures"]
    assert diff["non_claim"] == NON_CLAIM_NO_MASKING
