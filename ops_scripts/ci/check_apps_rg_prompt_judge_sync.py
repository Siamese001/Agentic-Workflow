#!/usr/bin/env python3
"""CI gate for apps_rg prompt/product-shape/X2/X1D sync.

Runs the focused regression suite that must pass whenever generated-lane
prompt, product-shape, validator, judge, or alignment-matrix surfaces change.

Bypass: ``APPS_RG_PROMPT_JUDGE_SYNC_BYPASS=1``
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TIMEOUT_SECONDS = 300

TEST_PATHS: tuple[str, ...] = (
    "tests/unit/apps_rg/test_section_prompt_judge_lockstep.py",
    "tests/unit/apps_rg/test_section_prompt_product_shape_drift.py",
    "tests/_apps_contract/test_section_x2_x1d_drift_ci.py",
    "tests/_apps_contract/test_apps_rg_x2_x1d_alignment.py",
    "tests/_apps_contract/test_x1d_judge_transport_parity_contract.py",
    "tests/unit/apps_rg/test_x1d_provider_transport_parity.py",
)


def _pytest_cmd() -> list[str]:
    return [sys.executable, "-m", "pytest", *TEST_PATHS, "-q"]


def main() -> int:
    if os.environ.get("APPS_RG_PROMPT_JUDGE_SYNC_BYPASS", "").strip() == "1":
        print("BYPASS - APPS_RG_PROMPT_JUDGE_SYNC_BYPASS=1")
        return 0

    cmd = _pytest_cmd()
    print("Running apps_rg prompt/judge sync gate:")
    print(" ".join(cmd))
    try:
        proc = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            check=False,
            timeout=TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        print(
            "FAIL - apps_rg prompt/product-shape/X2/X1D sync suite "
            f"timed out after {TIMEOUT_SECONDS}s"
        )
        return 124
    if proc.returncode == 0:
        print("OK - apps_rg prompt/product-shape/X2/X1D sync suite passed")
    else:
        print(f"FAIL - apps_rg prompt/product-shape/X2/X1D sync suite failed ({proc.returncode})")
    return int(proc.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
