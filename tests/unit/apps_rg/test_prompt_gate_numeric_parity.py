"""W4 (plan prompt-gate-ssot-consolidation-e7c9a2): Numeric parity gate.

Assert that every constraint number stated in judge rubric strings and YAML bullet
templates matches the corresponding SECTION_CONSTRAINTS value. Fails when any
drift is introduced between the SSOT and the compiled prompt/rubric text.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_prompt_gate_numeric_parity_passes() -> None:
    """check_prompt_gate_numeric_parity.py exits 0 on clean checkout."""
    gate = REPO_ROOT / "ops_scripts" / "ci" / "check_prompt_gate_numeric_parity.py"
    assert gate.exists(), f"gate not found: {gate}"
    result = subprocess.run(
        [sys.executable, str(gate)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        f"Numeric parity gate failed:\n{result.stdout}\n{result.stderr}"
    )
    assert "PASS" in result.stdout
