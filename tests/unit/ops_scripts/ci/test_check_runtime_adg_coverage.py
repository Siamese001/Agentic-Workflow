"""Tests for ``ops_scripts/ci/check_runtime_adg_coverage.py``.

Covers the audit subroutines and the SSOT integrity check added in the
runtime-OTEL-spec coverage harden pass. The gate is invoked as a subprocess
in some scenarios but here we exercise the public functions directly.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture(scope="module")
def gate_module():
    """Import the gate module fresh each test module."""
    spec = importlib.util.spec_from_file_location(  # type: ignore[attr-defined]
        "check_runtime_adg_coverage",
        REPO_ROOT / "ops_scripts" / "ci" / "check_runtime_adg_coverage.py",
    )
    mod = importlib.util.module_from_spec(spec)  # type: ignore[attr-defined]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


# ---------------------------------------------------------------------------
# Coverage subroutine
# ---------------------------------------------------------------------------


def test_compute_coverage_returns_three_emitters(gate_module) -> None:
    wired, total, results = gate_module.compute_coverage()
    assert total == 3
    assert wired == 3, results  # all three known emitters should be wired


# ---------------------------------------------------------------------------
# SSOT integrity check
# ---------------------------------------------------------------------------


def test_ssot_integrity_passes_in_clean_repo(gate_module) -> None:
    ok, problems = gate_module._check_tier2_ssot_integrity()
    assert ok, f"SSOT integrity failed unexpectedly: {problems}"
    assert problems == []


def test_tier1_covered_stages_are_three(gate_module) -> None:
    """The constitution: only stages 01, 09, 10 are Tier 1 covered."""
    assert set(gate_module._TIER1_COVERED_STAGES) == {
        "stage_01_trace_root",
        "stage_09_L2_execution",
        "stage_10_exit_eval",
    }


# ---------------------------------------------------------------------------
# main() exit codes
# ---------------------------------------------------------------------------


def test_main_audit_mode_returns_zero(gate_module, monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "argv", ["check_runtime_adg_coverage.py"])
    rc = gate_module.main()
    assert rc == 0
    out = capsys.readouterr().out
    assert "AUDIT" in out
    assert "wired=3/3" in out


def test_main_tier2_flag_prints_audits(gate_module, monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        sys, "argv", ["check_runtime_adg_coverage.py", "--tier2"]
    )
    rc = gate_module.main()
    assert rc == 0
    out = capsys.readouterr().out
    assert "[runtime-adg-coverage semconv SSOT]" in out
    assert "[runtime-adg-coverage Tier 2 spec]" in out
    assert "[runtime-adg-coverage Tier 2 emitters]" in out
    assert "[REGISTERED] stage_07_C0_retrieval" in out


def test_main_enforce_passes_when_clean(gate_module, monkeypatch) -> None:
    monkeypatch.setattr(
        sys, "argv", ["check_runtime_adg_coverage.py", "--enforce"]
    )
    rc = gate_module.main()
    assert rc == 0


def test_enforce_fails_when_ssot_integrity_broken(
    gate_module, monkeypatch, capsys
) -> None:
    """Simulate a broken SSOT and verify --enforce returns 1."""
    monkeypatch.setattr(
        gate_module,
        "_check_tier2_ssot_integrity",
        lambda: (False, ["fake problem for test"]),
    )
    monkeypatch.setattr(
        sys, "argv", ["check_runtime_adg_coverage.py", "--enforce"]
    )
    rc = gate_module.main()
    assert rc == 1
    err = capsys.readouterr().err
    assert "fake problem for test" in err
    assert "Tier 2 SSOT integrity failed" in err
