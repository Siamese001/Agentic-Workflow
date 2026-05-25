"""Cross-cutting hardening tests for graph-skills quality enhancement (W0–W10)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.fact_inventory.graph_skills_quality_enhancement_closeout import (
    BROWN_FIXTURE_PINS,
    LANES,
    brown_fixture_digests,
    build_closeout,
    build_d6_lane_matrix,
)
from apps_rg.runtime.graph_skill_phrase_capsule import SKILL_PHRASE_CAPSULE_MARKER
from apps_rg.runtime.graph_skills_utilization_scorer import score_graph_skills_utilization
from apps_rg.runtime.proof.x3_disposition_normalize import normalize_x3_code, normalize_x3_disposition
from apps_rg.runtime.validators.graph_skills_proof_common import (
    GraphSkillsProofError,
    assert_hybrid_fact_ids_in_resolver_pool,
)

REPO = Path(__file__).resolve().parents[3]


@pytest.mark.parametrize(
    ("raw", "expected", "live"),
    [
        ("X3_ALLOW", "ALLOW_FINISH", True),
        ("X3_BLOCK", "BLOCK", False),
        ("X3_REVIEW_SOFT_FAIL", "REVIEW", False),
        ("", "UNKNOWN", False),
    ],
)
def test_x3_normalization_matrix(raw: str, expected: str, live: bool) -> None:
    assert normalize_x3_code(raw) == expected
    norm = normalize_x3_disposition({"x3_code": raw, "pass": True})
    assert norm["x3_normalized"] == expected
    assert norm["live_x3_allow_claimed"] is (live and expected == "ALLOW_FINISH")


def test_brown_fixture_pins_match_disk() -> None:
    doc = brown_fixture_digests(REPO)
    assert doc["pass"] is True
    for row in doc["fixtures"]:
        assert row["actual_sha256"] == row["pinned_sha256"]


def test_closeout_matrix_covers_d1_d16() -> None:
    doc = build_closeout(REPO)
    ids = {r["dod_id"] for r in doc["proof_classification_matrix"]}
    assert ids == {f"D{i}" for i in range(1, 17)}
    assert doc["claims_release_eligible"] is False
    assert doc["claims_dynamic_graphrag_traverse"] is False
    d16 = next(r for r in doc["proof_classification_matrix"] if r["dod_id"] == "D16")
    assert d16["status"] == "BLOCKED"


def test_d6_lane_matrix_has_seven_lanes() -> None:
    rows = build_d6_lane_matrix(REPO)
    assert len(rows) == len(LANES)
    assert {r["lane"] for r in rows} == set(LANES)


def test_utilization_anti_gaming_requires_fact_and_phrase() -> None:
    row = {
        "skill_id": "sk_h",
        "allowed_phrases": ["platform engineering"],
        "fact_id_links": ["fact_h_001"],
        "graph_hop_path": ["jd", "headline", "sk_h"],
    }
    phrase_only = score_graph_skills_utilization(
        section_id="headline",
        skill_rows=[row],
        resume_display_text="Led platform-engineering programs.",
        text_claim_coverage={"sentences": [{"cited_fact_ids": []}]},
        allowed_fact_ids=["fact_h_001"],
    )
    assert phrase_only["pass"] is False
    grounded = score_graph_skills_utilization(
        section_id="headline",
        skill_rows=[row],
        resume_display_text="Led platform-engineering programs.",
        text_claim_coverage={"sentences": [{"cited_fact_ids": ["fact_h_001"]}]},
        allowed_fact_ids=["fact_h_001"],
    )
    assert grounded["pass"] is True


def test_hybrid_reorder_does_not_widen_pool() -> None:
    with pytest.raises(GraphSkillsProofError, match="outside resolver pool"):
        assert_hybrid_fact_ids_in_resolver_pool(
            section_id="executive_summary",
            hybrid_suggested_fact_ids=["fact_outside"],
            resolver_allowed_fact_ids=["fact_a", "fact_b"],
        )


def test_capsule_marker_constant() -> None:
    assert "NOT_EVIDENCE" in SKILL_PHRASE_CAPSULE_MARKER


def test_wave_receipts_w0_w9_exist() -> None:
    reports = REPO / "docs" / "reports" / "apps_rg"
    for n in range(10):
        path = reports / f"graph_skills_quality_w{n}_receipt.json"
        assert path.is_file(), f"missing {path.name}"


def test_neg6_capsule_not_in_allowed_fact_ids() -> None:
    from apps_rg.runtime.graph_skills_utilization_scorer import validate_scorer_inputs_neg6

    with pytest.raises(GraphSkillsProofError, match="capsule phrase"):
        validate_scorer_inputs_neg6(
            section_id="competencies",
            skill_rows=[{"skill_id": "s1", "allowed_phrases": ["forbidden token phrase"]}],
            allowed_fact_ids=["forbidden token phrase"],
        )
