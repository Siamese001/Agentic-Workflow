"""Tests for ops_scripts/ci/check_three_bucket_gap_thresholds.py (W5).

Plan: ``.windsurf/plans/three-bucket-gap-remediation-069806.md`` (W5).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
GATE = REPO_ROOT / "ops_scripts" / "ci" / "check_three_bucket_gap_thresholds.py"

__adg_consumer_mode__ = "inventory"


def _run_gate(*args: str, env: dict | None = None) -> tuple[int, str]:
    cmd = [sys.executable, str(GATE), *args]
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    proc = subprocess.run(
        cmd, capture_output=True, text=True, timeout=30, env=full_env, check=False
    )
    return proc.returncode, proc.stdout + proc.stderr


def _write_report(tmp_path: Path, classes: list[dict]) -> Path:
    """Write a synthetic gap report file. classes = list of class dicts."""
    report = {
        "report_kind": "ADG_THREE_BUCKET_GAP_REPORT",
        "snapshot": "synthetic.sqlite",
        "runtime_view_present": True,
        "total_edges_classified": sum(c.get("edge_count", 0) for c in classes),
        "health_score_pct_triplet_attested": 0.0,
        "summary_by_class": classes,
    }
    p = tmp_path / "synthetic_gap_report.json"
    p.write_text(json.dumps(report), encoding="utf-8")
    return p


def _all_zero_classes() -> list[dict]:
    return [
        {"defect_class": "TRIPLET_ATTESTED",  "severity": "—",  "edge_count": 0, "edge_pct": 0.0},
        {"defect_class": "REGISTRY_DRIFT",   "severity": "P2", "edge_count": 0, "edge_pct": 0.0},
        {"defect_class": "DEAD_PATH",        "severity": "P3", "edge_count": 0, "edge_pct": 0.0},
        {"defect_class": "UNOBSERVED_CODE",  "severity": "P3", "edge_count": 0, "edge_pct": 0.0},
        {"defect_class": "DYNAMIC_DISPATCH", "severity": "P5", "edge_count": 0, "edge_pct": 0.0},
        {"defect_class": "SHADOW_CHANNEL",   "severity": "P1", "edge_count": 0, "edge_pct": 0.0},
        {"defect_class": "CONFIG_BLOAT",     "severity": "P4", "edge_count": 0, "edge_pct": 0.0},
    ]


# ---------------------------------------------------------------------------
# Smoke
# ---------------------------------------------------------------------------


class TestSmoke:
    def test_clean_report_passes(self, tmp_path: Path):
        rpt = _write_report(tmp_path, _all_zero_classes())
        rc, out = _run_gate("--report", str(rpt))
        assert rc == 0
        assert "violations=0" in out

    def test_missing_report_fails_strict(self, tmp_path: Path):
        rc, out = _run_gate("--report", str(tmp_path / "nope.json"))
        assert rc == 1
        assert "report not found" in out

    def test_missing_report_advisory_passes(self, tmp_path: Path):
        rc, out = _run_gate(
            "--report", str(tmp_path / "nope.json"),
            env={"THREE_BUCKET_GAP_STRICT": "0"},
        )
        assert rc == 0


# ---------------------------------------------------------------------------
# Threshold violations
# ---------------------------------------------------------------------------


class TestThresholdViolations:
    def test_shadow_channel_nonzero_blocks_strict(self, tmp_path: Path):
        # SHADOW_CHANNEL has max_count=0; even 1 edge fails.
        classes = _all_zero_classes()
        for c in classes:
            if c["defect_class"] == "SHADOW_CHANNEL":
                c["edge_count"] = 1
                c["edge_pct"] = 0.0001
        rpt = _write_report(tmp_path, classes)
        rc, out = _run_gate("--report", str(rpt))
        assert rc == 1
        assert "SHADOW_CHANNEL" in out
        assert "violations=1" in out

    def test_shadow_channel_nonzero_advisory_passes(self, tmp_path: Path):
        classes = _all_zero_classes()
        for c in classes:
            if c["defect_class"] == "SHADOW_CHANNEL":
                c["edge_count"] = 5
        rpt = _write_report(tmp_path, classes)
        rc, _ = _run_gate(
            "--report", str(rpt), env={"THREE_BUCKET_GAP_STRICT": "0"}
        )
        assert rc == 0

    def test_registry_drift_above_5pct_blocks(self, tmp_path: Path):
        classes = _all_zero_classes()
        for c in classes:
            if c["defect_class"] == "REGISTRY_DRIFT":
                c["edge_pct"] = 5.5
                c["edge_count"] = 100
        rpt = _write_report(tmp_path, classes)
        rc, out = _run_gate("--report", str(rpt))
        assert rc == 1
        assert "REGISTRY_DRIFT" in out
        assert "5.5" in out or "5.50" in out

    def test_registry_drift_at_threshold_passes(self, tmp_path: Path):
        # Boundary check: edge_pct == max_pct must NOT trigger violation.
        classes = _all_zero_classes()
        for c in classes:
            if c["defect_class"] == "REGISTRY_DRIFT":
                c["edge_pct"] = 5.0
                c["edge_count"] = 100
        rpt = _write_report(tmp_path, classes)
        rc, _ = _run_gate("--report", str(rpt))
        assert rc == 0

    def test_unobserved_code_has_no_threshold(self, tmp_path: Path):
        # UNOBSERVED_CODE is exempt — never blocks even at 99.99%.
        classes = _all_zero_classes()
        for c in classes:
            if c["defect_class"] == "UNOBSERVED_CODE":
                c["edge_pct"] = 99.99
                c["edge_count"] = 400000
        rpt = _write_report(tmp_path, classes)
        rc, _ = _run_gate("--report", str(rpt))
        assert rc == 0

    def test_dynamic_dispatch_at_20pct_passes_above_blocks(self, tmp_path: Path):
        # 20% exact = pass; 20.5% = fail.
        classes = _all_zero_classes()
        for c in classes:
            if c["defect_class"] == "DYNAMIC_DISPATCH":
                c["edge_pct"] = 20.0
        rpt = _write_report(tmp_path, classes)
        assert _run_gate("--report", str(rpt))[0] == 0

        for c in classes:
            if c["defect_class"] == "DYNAMIC_DISPATCH":
                c["edge_pct"] = 20.5
        rpt = _write_report(tmp_path, classes)
        rc, _ = _run_gate("--report", str(rpt))
        assert rc == 1


# ---------------------------------------------------------------------------
# Bypass / strict-mode contract
# ---------------------------------------------------------------------------


class TestBypassAndStrictMode:
    def test_bypass_envvar_short_circuits(self, tmp_path: Path):
        # Even with violations + strict, bypass returns 0.
        classes = _all_zero_classes()
        for c in classes:
            if c["defect_class"] == "SHADOW_CHANNEL":
                c["edge_count"] = 100
        rpt = _write_report(tmp_path, classes)
        rc, out = _run_gate(
            "--report", str(rpt),
            env={"THREE_BUCKET_GAP_BYPASS": "1"},
        )
        assert rc == 0
        assert "bypass active" in out

    def test_strict_is_default_w5(self, tmp_path: Path):
        # No --strict flag, no env; gate must still block on a violation.
        classes = _all_zero_classes()
        for c in classes:
            if c["defect_class"] == "SHADOW_CHANNEL":
                c["edge_count"] = 1
        rpt = _write_report(tmp_path, classes)
        rc, out = _run_gate("--report", str(rpt))
        assert rc == 1
        assert "strict=True" in out


# ---------------------------------------------------------------------------
# Config override
# ---------------------------------------------------------------------------


class TestConfigOverride:
    def test_config_override_relaxes_thresholds(self, tmp_path: Path):
        # SHADOW_CHANNEL=10 violates default; pass with relaxed override.
        classes = _all_zero_classes()
        for c in classes:
            if c["defect_class"] == "SHADOW_CHANNEL":
                c["edge_count"] = 10
        rpt = _write_report(tmp_path, classes)
        cfg = tmp_path / "thresholds.json"
        cfg.write_text(
            json.dumps({"SHADOW_CHANNEL": {"max_count": 100, "max_pct": None}}),
            encoding="utf-8",
        )
        rc, _ = _run_gate("--report", str(rpt), "--config", str(cfg))
        assert rc == 0

    def test_config_override_tightens_thresholds(self, tmp_path: Path):
        # 0.5% REGISTRY_DRIFT is fine by default (5% cap), fails with 0.1% cap.
        classes = _all_zero_classes()
        for c in classes:
            if c["defect_class"] == "REGISTRY_DRIFT":
                c["edge_pct"] = 0.5
                c["edge_count"] = 50
        rpt = _write_report(tmp_path, classes)
        cfg = tmp_path / "tight.json"
        cfg.write_text(
            json.dumps({"REGISTRY_DRIFT": {"max_count": None, "max_pct": 0.1}}),
            encoding="utf-8",
        )
        rc, _ = _run_gate("--report", str(rpt), "--config", str(cfg))
        assert rc == 1


# ---------------------------------------------------------------------------
# W5 P5.2 — health_score floor enforcement
# ---------------------------------------------------------------------------


def _write_report_with_health(tmp_path: Path, classes: list[dict], health_pct: float) -> Path:
    """Variant of _write_report that lets us set health_score directly."""
    report = {
        "report_kind": "ADG_THREE_BUCKET_GAP_REPORT",
        "snapshot": "synthetic.sqlite",
        "runtime_view_present": True,
        "total_edges_classified": sum(c.get("edge_count", 0) for c in classes),
        "health_score_pct_triplet_attested": health_pct,
        "summary_by_class": classes,
    }
    p = tmp_path / "synthetic_gap_report.json"
    p.write_text(json.dumps(report), encoding="utf-8")
    return p


class TestHealthScoreFloor:
    def test_default_floor_is_zero_reporting_only(self, tmp_path: Path):
        """Default floor is 0.0 — health at any level above 0 passes."""
        rpt = _write_report_with_health(tmp_path, _all_zero_classes(), health_pct=1.5)
        rc, out = _run_gate("--report", str(rpt))
        assert rc == 0
        assert "health_floor=0.0%" in out

    def test_floor_cli_triggers_violation_when_below(self, tmp_path: Path):
        """--min-health-score forces a violation when health < floor."""
        rpt = _write_report_with_health(tmp_path, _all_zero_classes(), health_pct=45.0)
        rc, out = _run_gate("--report", str(rpt), "--min-health-score", "60")
        assert rc == 1
        assert "HEALTH_SCORE" in out
        assert "45.00%" in out and "60.00%" in out

    def test_floor_cli_passes_when_at_or_above(self, tmp_path: Path):
        """Health exactly at the floor passes (strict >, not >=)."""
        rpt = _write_report_with_health(tmp_path, _all_zero_classes(), health_pct=60.0)
        rc, _ = _run_gate("--report", str(rpt), "--min-health-score", "60")
        assert rc == 0

    def test_floor_env_var_triggers_violation(self, tmp_path: Path):
        """THREE_BUCKET_GAP_MIN_HEALTH_SCORE env var also activates the floor."""
        rpt = _write_report_with_health(tmp_path, _all_zero_classes(), health_pct=10.0)
        rc, out = _run_gate(
            "--report", str(rpt),
            env={"THREE_BUCKET_GAP_MIN_HEALTH_SCORE": "50.0"},
        )
        assert rc == 1
        assert "HEALTH_SCORE" in out

    def test_floor_cli_overrides_env(self, tmp_path: Path):
        """CLI flag takes precedence over env var."""
        rpt = _write_report_with_health(tmp_path, _all_zero_classes(), health_pct=70.0)
        # Env says floor=90 (would violate), CLI says floor=50 (would pass).
        rc, _ = _run_gate(
            "--report", str(rpt), "--min-health-score", "50",
            env={"THREE_BUCKET_GAP_MIN_HEALTH_SCORE": "90"},
        )
        assert rc == 0

    def test_floor_invalid_env_falls_back_to_zero(self, tmp_path: Path):
        """Malformed env var emits WARN + defaults to 0.0 (reporting only)."""
        rpt = _write_report_with_health(tmp_path, _all_zero_classes(), health_pct=1.0)
        rc, out = _run_gate(
            "--report", str(rpt),
            env={"THREE_BUCKET_GAP_MIN_HEALTH_SCORE": "notanumber"},
        )
        assert rc == 0
        assert "invalid THREE_BUCKET_GAP_MIN_HEALTH_SCORE" in out

    def test_floor_advisory_mode_exits_zero_on_health_violation(self, tmp_path: Path):
        """Advisory mode reports the health violation but exits 0."""
        rpt = _write_report_with_health(tmp_path, _all_zero_classes(), health_pct=10.0)
        rc, out = _run_gate(
            "--report", str(rpt), "--min-health-score", "50",
            env={"THREE_BUCKET_GAP_STRICT": "0"},
        )
        assert rc == 0
        assert "HEALTH_SCORE" in out

    def test_health_violation_written_to_report_file(self, tmp_path: Path):
        """Health-score violation appears in the JSON gate report."""
        rpt = _write_report_with_health(tmp_path, _all_zero_classes(), health_pct=10.0)
        _run_gate("--report", str(rpt), "--min-health-score", "50")
        gate_report = (
            REPO_ROOT / "docs" / "reports" / "adg" / "three_bucket_gap_gate_report.json"
        )
        d = json.loads(gate_report.read_text(encoding="utf-8"))
        assert any("HEALTH_SCORE" in v for v in d["violations"]), (
            f"health-score violation not in report: {d['violations']}"
        )


# ---------------------------------------------------------------------------
# Gate-report file schema
# ---------------------------------------------------------------------------


class TestGateReportSchema:
    def test_gate_report_keys_present(self, tmp_path: Path):
        rpt = _write_report(tmp_path, _all_zero_classes())
        _run_gate("--report", str(rpt))
        gate_report = (
            REPO_ROOT / "docs" / "reports" / "adg" / "three_bucket_gap_gate_report.json"
        )
        assert gate_report.exists()
        d = json.loads(gate_report.read_text(encoding="utf-8"))
        for k in (
            "gate", "tier", "timestamp", "report_path", "strict_mode",
            "classes", "violations", "status",
        ):
            assert k in d, f"gate report missing key: {k}"
        assert d["gate"] == "G-THREE-BUCKET-GAP"
        assert d["tier"] == "B"
