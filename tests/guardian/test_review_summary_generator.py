"""V15 P10.1 — Review Summary Generator Tests.

Validates deterministic markdown output, missing-file handling, and
approval decision logic using tmp_path fixtures with fake evidence JSON.
"""

from __future__ import annotations

import json
from pathlib import Path

from ops_scripts.review.generate_v15_review_summary import generate_summary

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# ===========================================================================
# Fixtures
# ===========================================================================


def _write_evidence(tmp_path: Path, phase: str, passed: int, violations: int, gate: str = "test_gate"):
    """Write a minimal evidence JSON fixture."""
    data = {
        "phase": phase,
        "gate": gate,
        "passed": passed,
        "violations": violations,
        "total_checks": passed + violations,
        "blocking": False,
        "passed_details": [],
        "violation_details": [{"check": f"check_{i}", "detail": f"violation {i}"} for i in range(violations)],
    }
    p = tmp_path / f"v15_{phase.lower()}_evidence.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def _write_guardian(tmp_path: Path, status: str = "PASS", total: int = 88, passed: int = 88, failed: int = 0):
    """Write a minimal guardian_report.json fixture."""
    data = {
        "status": status,
        "violations": [],
        "metadata": {
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": failed,
            "skipped_tests": 0,
            "failed_by_category": {},
        },
    }
    p = tmp_path / "guardian_report.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def _build_paths(tmp_path: Path, phases: list[str]):
    """Build evidence_files dict from tmp_path for given phases."""
    return {ph: tmp_path / f"v15_{ph.lower()}_evidence.json" for ph in phases}


# ===========================================================================
# A) Deterministic Content
# ===========================================================================


class TestDeterministicContent:
    """Validate fixed headings and key lines in generated markdown."""

    def test_all_present_all_pass(self, tmp_path):
        """All evidence + guardian present and passing."""
        for ph in ["P3", "P4", "P5", "P6"]:
            _write_evidence(tmp_path, ph, passed=5, violations=0, gate=f"gate_{ph.lower()}")
        gp = _write_guardian(tmp_path)

        ev = _build_paths(tmp_path, ["P3", "P4", "P5", "P6"])
        md, code = generate_summary(evidence_files=ev, guardian_report_paths=[gp])

        assert code == 0
        assert "# V15 Review Summary" in md
        assert "## 1. Inputs" in md
        assert "## 2. Gate Results" in md
        assert "## 3. Violation Details" in md
        assert "## 4. Guardian Report" in md
        assert "## 5. Approval Decision" in md
        assert "**Ready for human approval: YES**" in md
        assert "MISSING" not in md

    def test_headings_in_order(self, tmp_path):
        """Section headings appear in correct order."""
        for ph in ["P3", "P4", "P5", "P6"]:
            _write_evidence(tmp_path, ph, passed=3, violations=0)
        gp = _write_guardian(tmp_path)

        ev = _build_paths(tmp_path, ["P3", "P4", "P5", "P6"])
        md, _ = generate_summary(evidence_files=ev, guardian_report_paths=[gp])

        idx1 = md.index("## 1. Inputs")
        idx2 = md.index("## 2. Gate Results")
        idx3 = md.index("## 3. Violation Details")
        idx4 = md.index("## 4. Guardian Report")
        idx5 = md.index("## 5. Approval Decision")
        assert idx1 < idx2 < idx3 < idx4 < idx5

    def test_gate_table_rows(self, tmp_path):
        """Each phase gets a row in the gate results table."""
        for ph in ["P3", "P4", "P5", "P6"]:
            _write_evidence(tmp_path, ph, passed=4, violations=0, gate=f"gate_{ph}")
        gp = _write_guardian(tmp_path)

        ev = _build_paths(tmp_path, ["P3", "P4", "P5", "P6"])
        md, _ = generate_summary(evidence_files=ev, guardian_report_paths=[gp])

        for ph in ["P3", "P4", "P5", "P6"]:
            assert f"| {ph} |" in md

    def test_guardian_stats_shown(self, tmp_path):
        """Guardian report stats appear in output."""
        _write_evidence(tmp_path, "P3", passed=1, violations=0)
        gp = _write_guardian(tmp_path, total=100, passed=99, failed=1, status="FAIL")

        ev = _build_paths(tmp_path, ["P3"])
        md, _ = generate_summary(evidence_files=ev, guardian_report_paths=[gp])

        assert "**Total tests**: 100" in md
        assert "**Passed**: 99" in md
        assert "**Failed**: 1" in md


# ===========================================================================
# B) Violation Details
# ===========================================================================


class TestViolationDetails:
    """Violations from evidence must appear in section 3."""

    def test_violations_listed(self, tmp_path):
        """Violations appear with phase and check name."""
        _write_evidence(tmp_path, "P5", passed=4, violations=2, gate="authority")
        _write_evidence(tmp_path, "P3", passed=6, violations=0)
        gp = _write_guardian(tmp_path)

        ev = _build_paths(tmp_path, ["P3", "P5"])
        md, _ = generate_summary(evidence_files=ev, guardian_report_paths=[gp])

        assert "**P5** / `check_0`" in md
        assert "**P5** / `check_1`" in md

    def test_no_violations_message(self, tmp_path):
        """When no violations, explicit message shown."""
        _write_evidence(tmp_path, "P3", passed=5, violations=0)
        gp = _write_guardian(tmp_path)

        ev = _build_paths(tmp_path, ["P3"])
        md, _ = generate_summary(evidence_files=ev, guardian_report_paths=[gp])

        assert "No violations recorded." in md


# ===========================================================================
# C) Missing File Handling
# ===========================================================================


class TestMissingFileHandling:
    """Partial and total missing input scenarios."""

    def test_partial_missing_still_succeeds(self, tmp_path):
        """Some evidence missing: exit 0, MISSING shown in table."""
        _write_evidence(tmp_path, "P3", passed=5, violations=0)
        gp = _write_guardian(tmp_path)

        ev = _build_paths(tmp_path, ["P3", "P4", "P5", "P6"])
        md, code = generate_summary(evidence_files=ev, guardian_report_paths=[gp])

        assert code == 0
        assert "**Missing**: P4, P5, P6" in md
        assert "| P4 | — | — | — | — | MISSING |" in md

    def test_guardian_missing_still_succeeds(self, tmp_path):
        """Guardian report missing: exit 0, noted in output."""
        _write_evidence(tmp_path, "P3", passed=5, violations=0)

        ev = _build_paths(tmp_path, ["P3"])
        md, code = generate_summary(
            evidence_files=ev,
            guardian_report_paths=[tmp_path / "nonexistent.json"],
        )

        assert code == 0
        assert "**Guardian report**: missing" in md
        assert "Guardian report not available." in md

    def test_all_missing_exits_nonzero(self, tmp_path):
        """ALL inputs missing: exit 1."""
        ev = _build_paths(tmp_path, ["P3", "P4", "P5", "P6"])
        _, code = generate_summary(
            evidence_files=ev,
            guardian_report_paths=[tmp_path / "nonexistent.json"],
        )
        assert code == 1


# ===========================================================================
# D) Approval Decision Logic
# ===========================================================================


class TestApprovalDecision:
    """YES iff all gates pass AND guardian PASS; otherwise NO."""

    def test_all_pass_guardian_pass_yes(self, tmp_path):
        for ph in ["P3", "P4", "P5", "P6"]:
            _write_evidence(tmp_path, ph, passed=5, violations=0)
        gp = _write_guardian(tmp_path, status="PASS")

        ev = _build_paths(tmp_path, ["P3", "P4", "P5", "P6"])
        md, _ = generate_summary(evidence_files=ev, guardian_report_paths=[gp])
        assert "**Ready for human approval: YES**" in md

    def test_gate_violation_means_no(self, tmp_path):
        _write_evidence(tmp_path, "P3", passed=5, violations=0)
        _write_evidence(tmp_path, "P5", passed=4, violations=1)
        gp = _write_guardian(tmp_path, status="PASS")

        ev = _build_paths(tmp_path, ["P3", "P5"])
        md, _ = generate_summary(evidence_files=ev, guardian_report_paths=[gp])
        assert "**Ready for human approval: NO**" in md
        assert "gate failures" in md

    def test_guardian_fail_means_no(self, tmp_path):
        for ph in ["P3", "P4", "P5", "P6"]:
            _write_evidence(tmp_path, ph, passed=5, violations=0)
        gp = _write_guardian(tmp_path, status="FAIL", failed=2)

        ev = _build_paths(tmp_path, ["P3", "P4", "P5", "P6"])
        md, _ = generate_summary(evidence_files=ev, guardian_report_paths=[gp])
        assert "**Ready for human approval: NO**" in md
        assert "guardian report not PASS" in md

    def test_missing_evidence_means_no(self, tmp_path):
        _write_evidence(tmp_path, "P3", passed=5, violations=0)
        gp = _write_guardian(tmp_path, status="PASS")

        ev = _build_paths(tmp_path, ["P3", "P4"])
        md, _ = generate_summary(evidence_files=ev, guardian_report_paths=[gp])
        assert "**Ready for human approval: NO**" in md

    def test_guardian_missing_means_no(self, tmp_path):
        for ph in ["P3", "P4", "P5", "P6"]:
            _write_evidence(tmp_path, ph, passed=5, violations=0)

        ev = _build_paths(tmp_path, ["P3", "P4", "P5", "P6"])
        md, _ = generate_summary(
            evidence_files=ev,
            guardian_report_paths=[tmp_path / "nonexistent.json"],
        )
        assert "**Ready for human approval: NO**" in md


# ===========================================================================
# E) Determinism
# ===========================================================================


class TestDeterminism:
    """Same inputs must produce identical output."""

    def test_repeated_calls_identical(self, tmp_path):
        for ph in ["P3", "P4", "P5", "P6"]:
            _write_evidence(tmp_path, ph, passed=5, violations=0)
        gp = _write_guardian(tmp_path)

        ev = _build_paths(tmp_path, ["P3", "P4", "P5", "P6"])
        md1, _ = generate_summary(evidence_files=ev, guardian_report_paths=[gp])
        md2, _ = generate_summary(evidence_files=ev, guardian_report_paths=[gp])
        assert md1 == md2
