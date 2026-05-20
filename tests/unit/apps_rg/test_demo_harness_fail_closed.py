"""SP-002: executive_summary demo harness removed — no env hatch, no module CLI."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
REMOVED_MODULE = "apps_rg.runtime.dry_run.executive_summary_demo"


def test_demo_harness_module_no_longer_runnable() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", REMOVED_MODULE],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode != 0
