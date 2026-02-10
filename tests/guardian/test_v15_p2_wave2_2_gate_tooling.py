"""
Guardian test: Wave 2.2 Gate Tooling — subprocess tests for P2 evidence
collector, scoreboard P2 gate, and CI runner.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_SCRIPT = "ops_scripts/ci/v15_d_evidence_collect_p2.py"
SCOREBOARD_SCRIPT = "ops_scripts/ci/v15_coverage_scoreboard.py"
CI_RUNNER_SCRIPT = "ops_scripts/ci/run_v15_p2_gate.py"


class TestP2EvidenceCollector:
    """Subprocess tests for v15_d_evidence_collect_p2.py."""

    def test_evidence_collector_produces_valid_json(self, tmp_path: Path) -> None:
        """Evidence collector must produce valid JSON with schema 2.2.0."""
        out = tmp_path / "evidence.json"
        result = subprocess.run(
            [sys.executable, EVIDENCE_SCRIPT, "--repo-root", str(REPO_ROOT), "--output", str(out)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0, f"Evidence collector failed: {result.stderr}"
        assert out.exists(), "Evidence JSON not created"

        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["schema_version"] == "2.2.0"
        assert "entrypoints_total" in data
        assert "wired_count" in data
        assert "unwired_count" in data
        assert "already_enforced_count" in data
        assert "entries" in data
        assert isinstance(data["entries"], list)
        assert len(data["entries"]) == data["entrypoints_total"]

    def test_evidence_collector_all_wired(self, tmp_path: Path) -> None:
        """All unenforced entrypoints must be WIRED."""
        out = tmp_path / "evidence.json"
        result = subprocess.run(
            [sys.executable, EVIDENCE_SCRIPT, "--repo-root", str(REPO_ROOT), "--output", str(out)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0, f"Evidence collector failed: {result.stderr}"

        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["unwired_count"] == 0, f"Unwired entrypoints: {data.get('unwired_ids', [])}"

    def test_evidence_collector_synthetic_fail(self, tmp_path: Path) -> None:
        """With V15_P2_SYNTHETIC_FAIL=1, at least one entry must be UNWIRED."""
        out = tmp_path / "evidence.json"
        env = os.environ.copy()
        env["V15_P2_SYNTHETIC_FAIL"] = "1"
        result = subprocess.run(
            [sys.executable, EVIDENCE_SCRIPT, "--repo-root", str(REPO_ROOT), "--output", str(out)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            env=env,
        )
        assert result.returncode == 0, f"Evidence collector failed: {result.stderr}"

        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["unwired_count"] > 0, "Synthetic fail mode should produce unwired entries"

    def test_evidence_entries_have_required_fields(self, tmp_path: Path) -> None:
        """Every entry must have id, status, and evidence fields."""
        out = tmp_path / "evidence.json"
        result = subprocess.run(
            [sys.executable, EVIDENCE_SCRIPT, "--repo-root", str(REPO_ROOT), "--output", str(out)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0

        data = json.loads(out.read_text(encoding="utf-8"))
        for entry in data["entries"]:
            assert "id" in entry, f"Entry missing 'id': {entry}"
            assert "status" in entry, f"Entry missing 'status': {entry}"
            assert entry["status"] in ("WIRED", "UNWIRED", "ALREADY_ENFORCED"), (
                f"Invalid status: {entry['status']}"
            )
            assert "evidence" in entry, f"Entry missing 'evidence': {entry}"


class TestScoreboardP2Gate:
    """Subprocess tests for scoreboard --phase P2."""

    def test_p2_gate_passes_with_good_evidence(self, tmp_path: Path) -> None:
        """P2 gate must PASS when unwired_count == 0."""
        evidence = {
            "schema_version": "2.2.0",
            "inventory_sha256": "abc123",
            "entrypoints_total": 5,
            "wired_count": 3,
            "unwired_count": 0,
            "already_enforced_count": 2,
            "unwired_ids": [],
            "entries": [],
        }
        ev_path = tmp_path / "evidence.json"
        ev_path.write_text(json.dumps(evidence), encoding="utf-8")

        result = subprocess.run(
            [
                sys.executable,
                SCOREBOARD_SCRIPT,
                "--phase",
                "P2",
                "--p2-evidence",
                str(ev_path),
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0, f"P2 gate should PASS: {result.stdout}\n{result.stderr}"
        assert "PASS" in result.stdout

    def test_p2_gate_fails_with_unwired(self, tmp_path: Path) -> None:
        """P2 gate must FAIL when unwired_count > 0."""
        evidence = {
            "schema_version": "2.2.0",
            "inventory_sha256": "abc123",
            "entrypoints_total": 5,
            "wired_count": 2,
            "unwired_count": 1,
            "already_enforced_count": 2,
            "unwired_ids": ["A.test.fake"],
            "entries": [],
        }
        ev_path = tmp_path / "evidence.json"
        ev_path.write_text(json.dumps(evidence), encoding="utf-8")

        result = subprocess.run(
            [
                sys.executable,
                SCOREBOARD_SCRIPT,
                "--phase",
                "P2",
                "--p2-evidence",
                str(ev_path),
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode != 0, f"P2 gate should FAIL: {result.stdout}"
        assert "FAIL" in result.stdout

    def test_p2_gate_requires_evidence_arg(self) -> None:
        """P2 gate must fail if --p2-evidence is not provided."""
        result = subprocess.run(
            [
                sys.executable,
                SCOREBOARD_SCRIPT,
                "--phase",
                "P2",
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode != 0
        assert "P2 gate requires" in result.stderr


class TestP2CIRunner:
    """Subprocess tests for run_v15_p2_gate.py."""

    def test_ci_runner_passes(self) -> None:
        """CI runner must exit 0 when all entrypoints are wired."""
        result = subprocess.run(
            [sys.executable, CI_RUNNER_SCRIPT, "--repo-root", str(REPO_ROOT)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0, (
            f"CI runner should PASS:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert "PASSED" in result.stdout

    def test_ci_runner_synthetic_fail(self) -> None:
        """CI runner must exit non-zero under V15_P2_SYNTHETIC_FAIL=1."""
        env = os.environ.copy()
        env["V15_P2_SYNTHETIC_FAIL"] = "1"
        result = subprocess.run(
            [sys.executable, CI_RUNNER_SCRIPT, "--repo-root", str(REPO_ROOT)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            env=env,
        )
        assert result.returncode != 0, f"CI runner should FAIL under synthetic fail:\nstdout: {result.stdout}"
        assert "FAILED" in result.stdout
