"""W5 verification — observability skeleton smoke tests.

Plan: ``docs/archive/windsurf/legacy-tree/plans/apps-eval-harness-deferred-e4a1b7.md`` W5.P1-P3.

Proves the three skeletons run end-to-end against an empty (or populated)
ledger and produce shape-valid JSON outputs.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _run(script_path: Path, out_path: Path, extra_args: list[str] | None = None) -> int:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    args = [sys.executable, str(script_path), "--out", str(out_path)]
    if extra_args:
        args.extend(extra_args)
    result = subprocess.run(args, capture_output=True, text=True, timeout=60, check=False)
    if result.returncode != 0:
        print(f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    return result.returncode


class TestJudgeAgreementTracker:
    def test_produces_shape_valid_json(self, tmp_path: Path) -> None:
        script = REPO_ROOT / "ops_scripts" / "calibration" / "judge_agreement_tracker.py"
        out = tmp_path / "judge_agreement.json"
        rc = _run(script, out)
        assert rc == 0
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["skeleton"] is False  # promoted to real in DS-1 W4
        assert "per_app" in data
        assert "sample_size" in data
        assert "holdout_comparison" in data  # non-null after DS-1 W4 citation_quality holdout


class TestEvalTrendAnomalyDetector:
    def test_produces_shape_valid_json(self, tmp_path: Path) -> None:
        script = REPO_ROOT / "ops_scripts" / "calibration" / "eval_trend_anomaly_detector.py"
        out = tmp_path / "trend_anomalies.json"
        rc = _run(script, out)
        assert rc == 0
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["skeleton"] is True
        assert set(data["windows"].keys()) == {"1h", "6h", "24h"}
        assert isinstance(data["anomalies"], list)


class TestEvalHarnessWeeklyReport:
    def test_produces_json_and_markdown(self, tmp_path: Path) -> None:
        script = REPO_ROOT / "ops_scripts" / "calibration" / "eval_harness_weekly_report.py"
        json_out = tmp_path / "weekly.json"
        md_out = tmp_path / "weekly.md"
        args = [
            sys.executable, str(script),
            "--json-out", str(json_out),
            "--md-out", str(md_out),
        ]
        result = subprocess.run(args, capture_output=True, text=True, timeout=60, check=False)
        if result.returncode != 0:
            pytest.fail(f"weekly_report failed: stdout={result.stdout} stderr={result.stderr}")
        data = json.loads(json_out.read_text(encoding="utf-8"))
        assert "week" in data
        assert data["week"].startswith("20")  # e.g. "2026-Wxx"
        assert "per_app" in data
        md = md_out.read_text(encoding="utf-8")
        assert md.startswith("# Eval Harness Weekly Report")
