"""Contract gate W4.1: JD keyword → graph node link coverage.

For each JD admission check in graph_selection_rationale.json, asserts that
the fraction of admitted skills (fact-linked, not JD-inferred-only) meets a
minimum coverage floor.

A low admission rate is a graph staleness signal: the JD is naming capabilities
that exist in the JD vocabulary but have no fact-backed graph node.

Measurement: admitted_count / total_jd_checks >= ADMISSION_FLOOR (0.80)

Uses the Brown & Brown run artifact as the reference healthy run.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
_HEALTHY_RUN = REPO_ROOT / "artifacts/apps_rg/runtime_proofs/full_resume_f981c555d9e4"
_EXEC_LANE = _HEALTHY_RUN / "lanes" / "executive_summary"

HEALTHY_RUN_AVAILABLE = (
    (_EXEC_LANE / "graph_selection_rationale.json").exists()
)

# Minimum fraction of JD-checked skills that must be admitted (fact-linked)
# Violation = graph is stale relative to the JD vocabulary
JD_ADMISSION_FLOOR: float = 0.80


def _admission_rate(gsr: dict) -> tuple[float, int, int]:
    """Return (rate, admitted_count, total_checks) from a GSR dict."""
    checks = gsr.get("jd_only_admission_checks", [])
    if not isinstance(checks, list) or not checks:
        return 1.0, 0, 0
    admitted = sum(1 for c in checks if isinstance(c, dict) and c.get("admitted", False))
    return admitted / len(checks), admitted, len(checks)


# ---------------------------------------------------------------------------
# Unit-level: admission rate calculation
# ---------------------------------------------------------------------------

class TestAdmissionRateCalculation:
    def test_all_admitted(self) -> None:
        gsr = {
            "jd_only_admission_checks": [
                {"skill_id": "s1", "admitted": True},
                {"skill_id": "s2", "admitted": True},
            ]
        }
        rate, admitted, total = _admission_rate(gsr)
        assert rate == 1.0
        assert admitted == 2
        assert total == 2

    def test_none_admitted(self) -> None:
        gsr = {
            "jd_only_admission_checks": [
                {"skill_id": "s1", "admitted": False},
                {"skill_id": "s2", "admitted": False},
            ]
        }
        rate, admitted, total = _admission_rate(gsr)
        assert rate == 0.0
        assert admitted == 0

    def test_partial_admission(self) -> None:
        checks = [{"skill_id": f"s{i}", "admitted": i < 8} for i in range(10)]
        rate, admitted, total = _admission_rate({"jd_only_admission_checks": checks})
        assert abs(rate - 0.8) < 1e-9
        assert admitted == 8

    def test_empty_checks_returns_full_rate(self) -> None:
        rate, admitted, total = _admission_rate({"jd_only_admission_checks": []})
        assert rate == 1.0
        assert total == 0

    def test_missing_key_returns_full_rate(self) -> None:
        rate, admitted, total = _admission_rate({})
        assert rate == 1.0

    def test_floor_constant_is_sane(self) -> None:
        assert 0.5 <= JD_ADMISSION_FLOOR <= 1.0, "Floor must be between 0.5 and 1.0"


# ---------------------------------------------------------------------------
# Healthy artifact assertion
# ---------------------------------------------------------------------------

@pytest.mark.skipif(
    not HEALTHY_RUN_AVAILABLE,
    reason="Healthy Brown & Brown run artifacts not present",
)
class TestJdCoverageHealthyRun:
    def test_jd_admission_rate_above_floor(self) -> None:
        gsr = json.loads((_EXEC_LANE / "graph_selection_rationale.json").read_text())
        rate, admitted, total = _admission_rate(gsr)
        assert rate >= JD_ADMISSION_FLOOR, (
            f"JD admission rate {rate:.2%} ({admitted}/{total}) < floor {JD_ADMISSION_FLOOR:.0%}. "
            "Graph is stale relative to JD vocabulary — add fact-backed nodes for rejected skills."
        )

    def test_at_least_one_jd_check_present(self) -> None:
        gsr = json.loads((_EXEC_LANE / "graph_selection_rationale.json").read_text())
        checks = gsr.get("jd_only_admission_checks", [])
        assert len(checks) > 0, "GSR must contain at least one JD admission check"

    def test_rejected_skills_have_reason_codes(self) -> None:
        gsr = json.loads((_EXEC_LANE / "graph_selection_rationale.json").read_text())
        checks = gsr.get("jd_only_admission_checks", [])
        for c in checks:
            if not c.get("admitted", True):
                assert c.get("reason_code"), (
                    f"Rejected skill {c.get('skill_id')} missing reason_code"
                )


# ---------------------------------------------------------------------------
# Regression proof
# ---------------------------------------------------------------------------

class TestJdCoverageRegressionProof:
    def test_full_rejection_detected(self) -> None:
        """0% admission must fail the gate."""
        checks = [{"skill_id": f"s{i}", "admitted": False} for i in range(5)]
        rate, admitted, total = _admission_rate({"jd_only_admission_checks": checks})
        assert rate < JD_ADMISSION_FLOOR, (
            f"Full rejection (rate={rate:.2%}) should fail floor {JD_ADMISSION_FLOOR:.0%}"
        )

    def test_50pct_admission_fails_gate(self) -> None:
        """50% admission is below the 80% floor."""
        checks = [{"skill_id": f"s{i}", "admitted": i < 5} for i in range(10)]
        rate, _, _ = _admission_rate({"jd_only_admission_checks": checks})
        assert rate < JD_ADMISSION_FLOOR

    def test_95pct_admission_passes_gate(self) -> None:
        """95% is well above the floor — gate should pass."""
        checks = [{"skill_id": f"s{i}", "admitted": i < 19} for i in range(20)]
        rate, _, _ = _admission_rate({"jd_only_admission_checks": checks})
        assert rate >= JD_ADMISSION_FLOOR
