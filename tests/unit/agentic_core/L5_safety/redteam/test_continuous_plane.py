"""Tests for G11 ContinuousRedTeamPlane (Wave E impl)."""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.redteam import (
    ContinuousAssuranceReport,
    ContinuousRedTeamPlane,
    DEFAULT_PROBE_CORPUS,
    RedTeamProbe,
    default_plane,
)


def test_default_plane_runs_corpus_clean() -> None:
    """Out of the box, default plane + default corpus → all probes pass."""
    plane = default_plane()
    report = plane.run()
    assert isinstance(report, ContinuousAssuranceReport)
    assert report.total == len(DEFAULT_PROBE_CORPUS)
    assert report.failed == 0, f"Default corpus regressions: {[o for o in report.outcomes if not o.passed]}"
    assert report.hard_pass is True
    assert report.pass_rate == 1.0


def test_corpus_covers_both_surfaces() -> None:
    """The default corpus exercises both G13 (sanitizer) and G08 (firewall)."""
    surfaces = {p.surface for p in DEFAULT_PROBE_CORPUS}
    assert surfaces == {"sanitizer", "firewall"}


def test_corpus_has_hard_probes_for_credential_leaks() -> None:
    """Credential-leak probes MUST be HARD-tagged."""
    cred_probes = [p for p in DEFAULT_PROBE_CORPUS if "CRED" in p.probe_id]
    assert all(p.severity == "hard" for p in cred_probes)


def test_corpus_has_hard_probe_for_prompt_injection() -> None:
    inj = next(p for p in DEFAULT_PROBE_CORPUS if p.probe_id == "G13-INJ-001")
    assert inj.severity == "hard"
    assert inj.expected_outcome == "block"


def test_synthetic_failing_probe_is_reported() -> None:
    """A probe that EXPECTS block but the surface allows → registered as failure."""
    bad_probe = RedTeamProbe(
        probe_id="SYNTH-001",
        payload="Hello, this is benign text.",  # won't trigger anything
        surface="firewall",
        expected_outcome="block",  # mismatched expectation
        severity="hard",
    )
    plane = ContinuousRedTeamPlane(corpus=(bad_probe,))
    report = plane.run()
    assert report.failed == 1
    assert report.hard_pass is False
    assert "SYNTH-001" in report.hard_failures


def test_remediable_failure_does_not_break_hard_pass() -> None:
    """A failing REMEDIABLE probe leaves hard_pass=True."""
    soft_probe = RedTeamProbe(
        probe_id="SYNTH-002",
        payload="Benign text",
        surface="firewall",
        expected_outcome="block",
        severity="remediable",
    )
    plane = ContinuousRedTeamPlane(corpus=(soft_probe,))
    report = plane.run()
    assert report.failed == 1
    assert report.hard_pass is True  # remediable failures don't break hard pass
    assert report.hard_failures == ()


def test_pass_rate_calculation() -> None:
    p1 = RedTeamProbe(probe_id="X1", payload="ok", surface="firewall",
                       expected_outcome="pass", severity="remediable")
    p2 = RedTeamProbe(probe_id="X2", payload="hello", surface="firewall",
                       expected_outcome="pass", severity="remediable")
    p3 = RedTeamProbe(probe_id="X3", payload="benign", surface="firewall",
                       expected_outcome="block", severity="remediable")  # will fail
    plane = ContinuousRedTeamPlane(corpus=(p1, p2, p3))
    report = plane.run()
    assert report.total == 3
    assert report.passed == 2
    assert report.failed == 1
    assert abs(report.pass_rate - 2/3) < 1e-9


def test_outcomes_preserve_probe_ids() -> None:
    plane = default_plane()
    report = plane.run()
    reported_ids = {o.probe_id for o in report.outcomes}
    expected_ids = {p.probe_id for p in DEFAULT_PROBE_CORPUS}
    assert reported_ids == expected_ids


def test_empty_corpus_produces_trivially_passing_report() -> None:
    plane = ContinuousRedTeamPlane(corpus=())
    report = plane.run()
    assert report.total == 0
    assert report.pass_rate == 1.0  # empty → vacuously passes
    assert report.hard_pass is True


def test_run_is_deterministic() -> None:
    """Running the same plane twice yields identical reports."""
    plane = default_plane()
    a = plane.run()
    b = plane.run()
    assert a.total == b.total
    assert a.passed == b.passed
    assert a.hard_failures == b.hard_failures
    assert tuple((o.probe_id, o.passed) for o in a.outcomes) == \
           tuple((o.probe_id, o.passed) for o in b.outcomes)
