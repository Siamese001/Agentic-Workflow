"""
tests/runtime/test_proof_report_aggregator.py

Wfinal acceptance: validates the Phase 11 aggregate report.
"""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def report_md(proof_artifacts: Path) -> str:
    p = proof_artifacts / "proof_report.md"
    if not p.exists():
        pytest.fail(f"missing proof_report.md at {p}")
    return p.read_text(encoding="utf-8")


def test_proof_report_artifact_present(proof_artifacts: Path) -> None:
    assert (proof_artifacts / "proof_report.md").exists()


def test_proof_report_has_all_phase_sections(report_md: str) -> None:
    """Every phase 0 through 11 must have a section."""
    expected = (
        "Phase 0 -- Source Manifest",
        "Phase 1 -- Requirements Index",
        "Phase 2 + 3 -- Implementation Map and Coverage Matrix",
        "Phase 5 -- OTEL Trace Harness",
        "Phase 6 -- Deterministic Replay",
        "Phase 7 -- Anti-Bypass Negatives",
        "Phase 8 -- E2E Scenarios A through E",
        "Phase 9 -- Full prove_requirements CLI",
        "Phase 10 -- Spec-Named Tests",
        "Phase 11 -- This Report",
    )
    for header in expected:
        assert header in report_md, f"proof_report.md missing section: {header}"


def test_proof_report_acknowledges_zero_proven(report_md: str) -> None:
    """The constitutional honesty rule: PROVEN=0 must be stated explicitly."""
    assert "PROVEN" in report_md
    assert "remains 0" in report_md or "is 0" in report_md or "zero rows" in report_md


def test_proof_report_lists_all_five_scenarios(report_md: str) -> None:
    """A through E must all appear as scenarios."""
    for letter in ("A", "B", "C", "D", "E"):
        assert f"Scenario {letter}" in report_md, f"proof_report missing Scenario {letter}"


def test_proof_report_states_phase4_contract_only(report_md: str) -> None:
    """Phase 4 honesty: live-runtime wiring is explicitly NOT done."""
    assert "CONTRACT_ONLY" in report_md or "contract-only" in report_md
    assert "Phase 4" in report_md
    assert "not wired" in report_md.lower() or "not yet" in report_md.lower()


def test_proof_report_lists_anti_bypass_results(report_md: str) -> None:
    """Phase 7 must show the negatives_total and detected counts."""
    assert "negatives_total" in report_md
    assert "negatives_detected" in report_md
    assert "negatives_escaped" in report_md


def test_proof_report_lists_replay_match(report_md: str) -> None:
    assert "all_scenarios_match" in report_md


def test_proof_report_acknowledges_w7_emitter_status(report_md: str) -> None:
    """The W7 OTEL emitter adapter must be cited as ready-but-not-wired."""
    assert "RuntimeSpanEmitter" in report_md or "otel_emitter" in report_md
    assert "ready" in report_md.lower() or "READY" in report_md


def test_proof_report_includes_honest_gaps_section(report_md: str) -> None:
    assert "Honest Gaps" in report_md or "honest gaps" in report_md.lower()
