"""Tests for scorecard auto-update in ops_scripts/ci/infra_wiring_scan.py"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ops_scripts.ci.infra_wiring_scan import (
    _classify_violations,
    update_scorecard,
)


class TestClassifyViolations:
    """Tests for _classify_violations()."""

    def test_empty_violations_returns_empty(self) -> None:
        """Happy path: no violations → empty details list."""
        assert _classify_violations({}) == []

    def test_extracts_infra_from_import_pattern(self) -> None:
        """Happy path: extracts infra name from 'import X' pattern."""
        violations = {
            "C:\\Git\\repo\\apps_eval\\services\\bad.py": [(6, "import sqlite3")],
        }
        details = _classify_violations(violations)
        assert len(details) == 1
        assert details[0]["infra"] == "sqlite3"

    def test_extracts_infra_from_from_pattern(self) -> None:
        """Happy path: extracts infra name from 'from X' pattern."""
        violations = {
            "C:\\Git\\repo\\apps_lic\\types\\bad.py": [(10, "from chromadb")],
        }
        details = _classify_violations(violations)
        assert len(details) == 1
        assert details[0]["infra"] == "chromadb"

    def test_short_path_extraction(self) -> None:
        """Edge case: relative path starts at apps_* or agentic_core."""
        violations = {
            "C:\\Git\\Agentic-Workflow\\apps_rg\\services\\svc.py": [(1, "import redis")],
        }
        details = _classify_violations(violations)
        assert "apps_rg" in details[0]["file"]

    def test_multiple_violations_in_same_file(self) -> None:
        """Edge case: multiple violations in one file produce multiple detail records."""
        violations = {
            "C:\\Git\\repo\\apps_eval\\svc.py": [(1, "import redis"), (2, "import sqlite3")],
        }
        details = _classify_violations(violations)
        assert len(details) == 2


class TestUpdateScorecard:
    """Tests for update_scorecard()."""

    def test_creates_scorecard_file(self, tmp_path: Path) -> None:
        """Happy path: scorecard file is created when violations exist."""
        artifacts = tmp_path / "artifacts"
        artifacts.mkdir()
        violations = {
            str(tmp_path / "apps_eval" / "bad.py"): [(6, "import sqlite3")],
        }
        update_scorecard(tmp_path, violations)
        scorecard_path = artifacts / "infra_wiring_scorecard.json"
        assert scorecard_path.exists()
        data = json.loads(scorecard_path.read_text(encoding="utf-8"))
        assert data["violations"]["p0"] == 1
        assert data["compliance_score"] < 100

    def test_zero_violations_gives_100_compliance(self, tmp_path: Path) -> None:
        """Happy path: no violations → 100% compliance score."""
        (tmp_path / "artifacts").mkdir()
        update_scorecard(tmp_path, {})
        data = json.loads(
            (tmp_path / "artifacts" / "infra_wiring_scorecard.json").read_text(encoding="utf-8")
        )
        assert data["violations"]["p0"] == 0
        assert data["compliance_score"] == 100
        assert data["ratchets"][0]["status"] == "COMPLIANT"

    def test_scorecard_has_timestamp(self, tmp_path: Path) -> None:
        """Verification: scorecard includes a fresh timestamp."""
        (tmp_path / "artifacts").mkdir()
        update_scorecard(tmp_path, {})
        data = json.loads(
            (tmp_path / "artifacts" / "infra_wiring_scorecard.json").read_text(encoding="utf-8")
        )
        assert "timestamp" in data
        assert "T" in data["timestamp"]

    def test_scorecard_overwrites_existing(self, tmp_path: Path) -> None:
        """Edge case: re-running overwrites the scorecard with fresh data."""
        (tmp_path / "artifacts").mkdir()
        # First run with violations
        update_scorecard(tmp_path, {str(tmp_path / "apps_eval" / "x.py"): [(1, "import redis")]})
        # Second run with no violations
        update_scorecard(tmp_path, {})
        data = json.loads(
            (tmp_path / "artifacts" / "infra_wiring_scorecard.json").read_text(encoding="utf-8")
        )
        assert data["violations"]["p0"] == 0
        assert data["compliance_score"] == 100

    def test_p0_details_populated(self, tmp_path: Path) -> None:
        """Happy path: p0_details matches violation count."""
        (tmp_path / "artifacts").mkdir()
        violations = {
            str(tmp_path / "apps_eval" / "a.py"): [(1, "import redis")],
            str(tmp_path / "apps_rg" / "b.py"): [(2, "import sqlite3")],
        }
        update_scorecard(tmp_path, violations)
        data = json.loads(
            (tmp_path / "artifacts" / "infra_wiring_scorecard.json").read_text(encoding="utf-8")
        )
        assert len(data["p0_details"]) == 2
        assert data["violations"]["p0"] == 2
