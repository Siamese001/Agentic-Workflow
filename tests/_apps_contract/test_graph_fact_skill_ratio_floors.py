"""Contract gate: fact-to-skill ratio floors for graph grounding quality.

Tests two measurement points for each section:
  GSR = graph_selection_rationale.json::allowed_fact_count / selected_skill_count
        (pre-C0.3 — initial graph selection outcome)
  C03 = native_c03_final_evidence.json::len(selected_source_fact_ids) / selected_skill_count
        (post-C0.3 — facts that actually reach the LLM)

Healthy run assertions use the real Brown & Brown run artifact.
Regression proof uses injected fixture to confirm the gate fails on collapse.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.graph.ratio_floor_policy import (
    DEFAULT_C03_FLOOR,
    DEFAULT_GSR_FLOOR,
    check_c03_ratio,
    check_gsr_ratio,
    c03_floor,
    gsr_floor,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

# Known healthy run with confirmed GSR/C03 data
_HEALTHY_RUN = REPO_ROOT / "artifacts/apps_rg/runtime_proofs/full_resume_f981c555d9e4"
_EXEC_LANE = _HEALTHY_RUN / "lanes" / "executive_summary"

HEALTHY_RUN_AVAILABLE = _EXEC_LANE.is_dir() and (
    (_EXEC_LANE / "graph_selection_rationale.json").exists()
    and (_EXEC_LANE / "native_c03_final_evidence.json").exists()
)


# ---------------------------------------------------------------------------
# Unit-level: floor policy module
# ---------------------------------------------------------------------------

class TestFloorPolicy:
    def test_all_known_sections_have_gsr_floors(self) -> None:
        sections = [
            "executive_summary",
            "competencies",
            "headline",
            "ibm_bullets",
            "ibm_narrative",
            "unify_bullets",
            "unify_narrative",
        ]
        for sec in sections:
            assert gsr_floor(sec) > 0, f"GSR floor must be positive for {sec}"

    def test_all_known_sections_have_c03_floors(self) -> None:
        sections = [
            "executive_summary",
            "competencies",
            "headline",
            "ibm_bullets",
            "ibm_narrative",
            "unify_bullets",
            "unify_narrative",
        ]
        for sec in sections:
            assert c03_floor(sec) > 0, f"C03 floor must be positive for {sec}"

    def test_unknown_section_uses_defaults(self) -> None:
        assert gsr_floor("unknown_section") == DEFAULT_GSR_FLOOR
        assert c03_floor("unknown_section") == DEFAULT_C03_FLOOR

    def test_c03_floor_always_leq_gsr_floor(self) -> None:
        """C03 is downstream of GSR; C03 floor must not exceed GSR floor."""
        sections = [
            "executive_summary",
            "competencies",
            "headline",
            "ibm_bullets",
            "ibm_narrative",
            "unify_bullets",
            "unify_narrative",
        ]
        for sec in sections:
            assert c03_floor(sec) <= gsr_floor(sec), (
                f"C03 floor ({c03_floor(sec)}) must be ≤ GSR floor ({gsr_floor(sec)}) for {sec}"
            )

    def test_check_gsr_ratio_passes_at_floor(self) -> None:
        passes, ratio, floor = check_gsr_ratio(
            "executive_summary",
            allowed_fact_count=7,
            selected_skill_count=20,
        )
        assert passes, f"ratio={ratio:.2f} floor={floor:.2f}"

    def test_check_gsr_ratio_fails_below_floor(self) -> None:
        passes, ratio, floor = check_gsr_ratio(
            "executive_summary",
            allowed_fact_count=1,
            selected_skill_count=20,
        )
        assert not passes, f"Expected fail: ratio={ratio:.2f} floor={floor:.2f}"

    def test_check_c03_ratio_passes_at_floor(self) -> None:
        passes, ratio, floor = check_c03_ratio(
            "executive_summary",
            fact_count=7,
            selected_skill_count=20,
        )
        assert passes, f"ratio={ratio:.2f} floor={floor:.2f}"

    def test_check_c03_ratio_fails_below_floor(self) -> None:
        passes, ratio, floor = check_c03_ratio(
            "executive_summary",
            fact_count=0,
            selected_skill_count=20,
        )
        assert not passes, f"Expected fail: ratio={ratio:.2f} floor={floor:.2f}"

    def test_zero_skill_count_never_fails(self) -> None:
        """Division-by-zero guard: 0 selected skills → skip ratio check."""
        passes, ratio, floor = check_gsr_ratio(
            "executive_summary",
            allowed_fact_count=0,
            selected_skill_count=0,
        )
        assert passes
        assert ratio == 0.0

    def test_zero_skill_count_c03_never_fails(self) -> None:
        passes, ratio, floor = check_c03_ratio(
            "executive_summary",
            fact_count=0,
            selected_skill_count=0,
        )
        assert passes
        assert ratio == 0.0


# ---------------------------------------------------------------------------
# Healthy artifact assertions
# ---------------------------------------------------------------------------

@pytest.mark.skipif(
    not HEALTHY_RUN_AVAILABLE,
    reason="Healthy Brown & Brown run artifacts not present",
)
class TestHealthyRunRatios:
    def test_gsr_ratio_above_floor_exec_summary(self) -> None:
        gsr = json.loads((_EXEC_LANE / "graph_selection_rationale.json").read_text())
        skill_ct = gsr.get("selected_skill_count", 0)
        fact_ct = gsr.get("allowed_fact_count", 0)
        passes, ratio, floor = check_gsr_ratio(
            "executive_summary",
            allowed_fact_count=fact_ct,
            selected_skill_count=skill_ct,
        )
        assert passes, (
            f"GSR ratio {ratio:.3f} < floor {floor:.3f} for executive_summary. "
            f"skills={skill_ct} facts={fact_ct}. Graph funnel collapse detected."
        )

    def test_c03_ratio_above_floor_exec_summary(self) -> None:
        gsr = json.loads((_EXEC_LANE / "graph_selection_rationale.json").read_text())
        c03 = json.loads((_EXEC_LANE / "native_c03_final_evidence.json").read_text())
        skill_ct = gsr.get("selected_skill_count", 0)
        fact_ct = len(c03.get("selected_source_fact_ids", []))
        passes, ratio, floor = check_c03_ratio(
            "executive_summary",
            fact_count=fact_ct,
            selected_skill_count=skill_ct,
        )
        assert passes, (
            f"C03 ratio {ratio:.3f} < floor {floor:.3f} for executive_summary. "
            f"skills={skill_ct} facts={fact_ct}. C0.3 hop traversal collapse detected."
        )

    def test_gsr_fact_count_nonzero(self) -> None:
        gsr = json.loads((_EXEC_LANE / "graph_selection_rationale.json").read_text())
        assert gsr.get("allowed_fact_count", 0) > 0, "GSR must have at least 1 allowed fact"

    def test_c03_fact_ids_nonzero(self) -> None:
        c03 = json.loads((_EXEC_LANE / "native_c03_final_evidence.json").read_text())
        assert len(c03.get("selected_source_fact_ids", [])) > 0, (
            "C03 must have at least 1 selected fact ID"
        )


# ---------------------------------------------------------------------------
# Regression proof — injected collapse MUST fail the gate
# ---------------------------------------------------------------------------

class TestRegressionProof:
    """These tests MUST fail on injected collapse to prove the gate is live."""

    def test_injected_gsr_collapse_detected(self, tmp_path: Path) -> None:
        """Inject a GSR with 1 fact for 20 skills (ratio=0.05) — must fail."""
        passes, ratio, floor = check_gsr_ratio(
            "executive_summary",
            allowed_fact_count=1,
            selected_skill_count=20,
        )
        assert not passes, (
            f"GATE FAILURE: injected collapse (ratio={ratio:.2f}) was not caught "
            f"by floor={floor:.2f}. Gate is not enforcing floor correctly."
        )

    def test_injected_c03_collapse_detected(self, tmp_path: Path) -> None:
        """Inject a C03 with 0 facts for 15 skills (ratio=0.0) — must fail."""
        passes, ratio, floor = check_c03_ratio(
            "executive_summary",
            fact_count=0,
            selected_skill_count=15,
        )
        assert not passes, (
            f"GATE FAILURE: injected C03 collapse (ratio={ratio:.2f}) was not caught "
            f"by floor={floor:.2f}."
        )

    def test_injected_headline_gsr_collapse_detected(self) -> None:
        """Headline has a stricter floor (0.45) — collapse with 1/10 must fail."""
        passes, ratio, floor = check_gsr_ratio(
            "headline",
            allowed_fact_count=1,
            selected_skill_count=10,
        )
        assert not passes, (
            f"GATE FAILURE: headline GSR collapse not caught (ratio={ratio:.2f} floor={floor:.2f})"
        )

    def test_valid_ratio_passes_sanity(self) -> None:
        """Confirm a clearly healthy ratio passes — guards against always-true gate."""
        passes, ratio, floor = check_gsr_ratio(
            "executive_summary",
            allowed_fact_count=10,
            selected_skill_count=20,
        )
        assert passes, f"Clearly healthy ratio {ratio:.2f} should pass floor {floor:.2f}"
