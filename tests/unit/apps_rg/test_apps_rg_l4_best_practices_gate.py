"""apps-test-model: APP CONTRACT.

CI gate coverage for apps_rg R1B/L4 best-practice invariants.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_apps_rg_l4_best_practices_gate_passes() -> None:
    root = Path(__file__).resolve().parents[3]
    result = subprocess.run(
        [sys.executable, "ops_scripts/ci/check_apps_rg_l4_best_practices.py"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "[check_apps_rg_l4_best_practices] PASS" in result.stdout
