"""Tests for ops_scripts/ci/check_adg_certified.py.

Tier: unit
Plan: .windsurf/plans/three-bucket-otel-view-5db409.md (W7)
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
GATE = REPO_ROOT / "ops_scripts" / "ci" / "check_adg_certified.py"
VERDICT_PATH = REPO_ROOT / "docs" / "reports" / "adg" / "ADG_CERTIFIED_VERDICT.json"

__adg_consumer_mode__ = "inventory"


def _run(*args: str) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(GATE), *args],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO_ROOT,
        check=False,
    )
    return proc.returncode, proc.stdout + proc.stderr


class TestAdvisoryMode:
    def test_advisory_returns_zero(self) -> None:
        rc, out = _run()
        assert rc == 0
        assert "verdict=" in out
        assert "sub_gates_run=" in out

    def test_writes_verdict_file(self) -> None:
        _run()
        assert VERDICT_PATH.exists()
        data = json.loads(VERDICT_PATH.read_text(encoding="utf-8"))
        assert data["gate"] == "G-ADG-CERTIFIED"
        assert data["verdict"] in ("ADG_CERTIFIED", "ADG_NOT_CERTIFIED")
        assert "sub_gates" in data
        assert isinstance(data["sub_gates"], list)
        assert len(data["sub_gates"]) >= 4


class TestStrictMode:
    def test_strict_runs_and_reports(self) -> None:
        # Strict mode: with current snapshot in CERTIFIED state, this passes.
        # If certification is broken, this returns 1. Either is acceptable
        # for the test — we just verify the gate produces structured output.
        rc, out = _run("--strict")
        assert rc in (0, 1)
        assert "verdict=" in out
        assert "strict=True" in out


class TestVerdictSchema:
    def test_verdict_keys_complete(self) -> None:
        _run()
        data = json.loads(VERDICT_PATH.read_text(encoding="utf-8"))
        for key in (
            "gate",
            "tier",
            "verdict",
            "strict_mode",
            "timestamp",
            "snapshot_used",
            "blockers",
            "sub_gates",
        ):
            assert key in data, f"missing key {key}"

    def test_each_subgate_has_label_and_ok(self) -> None:
        _run()
        data = json.loads(VERDICT_PATH.read_text(encoding="utf-8"))
        for sg in data["sub_gates"]:
            assert "label" in sg
            assert "ok" in sg
            assert isinstance(sg["ok"], bool)
