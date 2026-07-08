from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.apps_test_model("GOVERNANCE STATIC")

REPO_ROOT = Path(__file__).resolve().parents[2]
SCANNER = REPO_ROOT / "ops_scripts" / "ci" / "check_apps_rg_l5_no_authority_widening.py"
WIRING_SCANNER = REPO_ROOT / "ops_scripts" / "ci" / "check_apps_rg_l5_packet_runtime_wiring.py"


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )


def test_l5_authority_boundary_scanner_passes_repo() -> None:
    result = _run(str(SCANNER))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "gate GREEN" in result.stdout


def test_l5_runtime_wiring_scanner_passes_repo() -> None:
    result = _run(str(WIRING_SCANNER))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "runtime L5 packet wiring gate GREEN" in result.stdout


def test_l5_authority_boundary_scanner_fails_l5_packet_gate_ref_fixture(tmp_path: Path) -> None:
    fixture = tmp_path / "bad_gate_ref.py"
    fixture.write_text(
        "def build():\n"
        "    return dict(gate_verdict_refs=('l5_certification_packet:bad',))\n",
        encoding="utf-8",
    )

    result = _run(str(SCANNER), "--extra-path", str(fixture))

    assert result.returncode == 1
    assert "L5 packet ref placed in gate_verdict_refs" in result.stdout
