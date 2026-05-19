"""W5-W7 aggregation product-proof policy unit tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.aggregation.review_lane_policy import evaluate_review_lane_policy
from apps_rg.runtime.aggregation.cross_section_x2 import (
    CrossSectionGateResult,
    VERDICT_PASS,
    VERDICT_WARN,
    _overlap_class_fully_dispositioned,
)
from apps_rg.runtime.aggregation.warn_policy import (
    VERDICT_FAIL,
    cross_section_product_pass,
    evaluate_warn_policy,
)
from apps_rg.runtime.locked_copy.locked_copy_manifest import find_repo_root
from apps_rg.runtime.reports.generated_lane_rollup import GENERATED_LANES

REPO = find_repo_root()


def test_overlap_dispositioned_exact_duplicate_passes_product() -> None:
    decisions = [
        {"overlap_class": "exact_duplicate", "removed_section": "ibm_bullets", "kept_section": "headline"},
    ]
    removed = [
        {
            "overlap_class": "exact_duplicate",
            "disposition": "removed",
            "provenance_retained": True,
        },
    ]
    assert _overlap_class_fully_dispositioned(decisions, removed, "exact_duplicate") is True
    gates = [
        CrossSectionGateResult(
            "x2_cross_section_exact_duplicate",
            VERDICT_PASS,
            decisive_reason="dispositioned",
        ),
    ]
    assert cross_section_product_pass(gates) is True


def test_warn_policy_warn_blocks_product_not_structural() -> None:
    gates = [
        CrossSectionGateResult("x2_cross_section_exact_duplicate", VERDICT_WARN, observed=1),
        CrossSectionGateResult("x2_cross_section_metric_collision", VERDICT_PASS),
    ]
    wp = evaluate_warn_policy(cross_gates=gates)
    assert wp["structural_cross_section_eligible"] is True
    assert wp["product_allow_blocked_by_cross_section"] is True
    assert cross_section_product_pass(gates) is False


def test_review_lane_policy_mock_not_product_allow() -> None:
    rollup = {
        "rollup_id": "t",
        "lanes": {
            lk: {
                "x3_code": "X3_REVIEW_MOCKED_PLUMBING_ONLY",
                "latest_successful_real_artifact_path": "artifacts/apps_rg/runtime_proofs/headline/real/x",
            }
            for lk in GENERATED_LANES
        },
    }
    policy = evaluate_review_lane_policy(repo=REPO, rollup_blob=rollup)
    assert policy["summary"]["product_allow_claimed"] is False
    assert policy["summary"]["product_review_required"] is True
    assert all(p["disposition_class"] == "MOCK_PLUMBING_ONLY" for p in policy["per_lane"])


@pytest.mark.skipif(
    not (REPO / "artifacts/apps_rg/runtime_proofs/generated_lane_rollup/generated_lane_rollup.json").is_file(),
    reason="coherent rollup not built",
)
def test_coherent_rollup_policy_artifact_fields() -> None:
    asm = REPO / "artifacts/apps_rg/runtime_proofs/final_resume_assembly"
    for name in (
        "coherent_rollup_policy.json",
        "review_lane_policy.json",
        "final_resume_receipt.json",
    ):
        p = asm / name
        assert p.is_file(), name
        blob = json.loads(p.read_text(encoding="utf-8"))
        assert blob
