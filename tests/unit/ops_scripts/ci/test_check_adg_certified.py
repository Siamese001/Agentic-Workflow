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


def _run(*args: str, env_extra: dict[str, str] | None = None) -> tuple[int, str]:
    run_env = os.environ.copy()
    # Neutralize caller-inherited strict/bypass so each test starts clean.
    run_env.pop("ADG_CERTIFIED_STRICT", None)
    run_env.pop("ADG_CERTIFIED_BYPASS", None)
    if env_extra:
        run_env.update(env_extra)
    proc = subprocess.run(
        [sys.executable, str(GATE), *args],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO_ROOT,
        check=False,
        env=run_env,
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


# W6 P6.1 completion-audit (2026-04-30): env-var surface matches the rest
# of the 3B-tier gates. These tests pin that surface.
class TestEnvVarSurface:
    def test_adg_certified_strict_env_activates_strict(self) -> None:
        """ADG_CERTIFIED_STRICT=1 flips strict without requiring --strict."""
        rc, out = _run(env_extra={"ADG_CERTIFIED_STRICT": "1"})
        assert rc in (0, 1)
        assert "strict=True" in out, (
            f"env var did not activate strict; got: {out!r}"
        )

    def test_adg_certified_strict_env_zero_stays_advisory(self) -> None:
        """Only the literal '1' activates — mirrors L2 pilot strictness."""
        for value in ("0", "", "true", "yes", "ON"):
            rc, out = _run(env_extra={"ADG_CERTIFIED_STRICT": value})
            assert "strict=False" in out, (
                f"value {value!r} should NOT activate strict; got: {out!r}"
            )

    def test_adg_certified_bypass_env_skips_gate(self) -> None:
        """ADG_CERTIFIED_BYPASS=1 short-circuits the whole gate, exits 0."""
        rc, out = _run(env_extra={"ADG_CERTIFIED_BYPASS": "1"})
        assert rc == 0
        assert "bypass active" in out
        # No sub-gate output when bypassed.
        assert "sub_gates_run=" not in out

    def test_adg_certified_bypass_beats_strict(self) -> None:
        """BYPASS is evaluated first — both env vars set => bypass wins."""
        rc, out = _run(env_extra={
            "ADG_CERTIFIED_BYPASS": "1",
            "ADG_CERTIFIED_STRICT": "1",
        })
        assert rc == 0
        assert "bypass active" in out

    def test_cli_strict_still_works(self) -> None:
        """--strict CLI flag remains functional after env-var addition."""
        rc, out = _run("--strict")
        assert rc in (0, 1)
        assert "strict=True" in out

    def test_cli_strict_and_env_strict_both_ok(self) -> None:
        """Setting both --strict and ADG_CERTIFIED_STRICT=1 is valid."""
        rc, out = _run("--strict", env_extra={"ADG_CERTIFIED_STRICT": "1"})
        assert rc in (0, 1)
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
