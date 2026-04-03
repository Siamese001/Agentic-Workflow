"""Testing accelerator proxy module.

Delegates to the unified adg_test.py tool.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent


def run_gap_analysis(top: int = 20, layer: str | None = None) -> int:
    """Run gap analysis using adg_test.py."""
    cmd = [sys.executable, "tools/adg/adg_test.py", "gap", "--top", str(top)]
    if layer:
        cmd.extend(["--layer", layer])
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


def run_scope_analysis(changed: list[str]) -> int:
    """Run scope analysis using adg_test.py."""
    cmd = [sys.executable, "tools/adg/adg_test.py", "scope"] + changed
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


def run_test_check(json_output: str | None = None) -> int:
    """Run collection safety check using adg_test.py."""
    cmd = [sys.executable, "tools/adg/adg_test.py", "check"]
    if json_output:
        cmd.extend(["--json", json_output])
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


def run_preflight(strict: bool = False, quick: bool = True) -> int:
    """Run preflight check using adg_test.py."""
    cmd = [sys.executable, "tools/adg/adg_test.py", "preflight"]
    if strict:
        cmd.append("--strict")
    if quick:
        cmd.append("--quick")
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


__all__ = [
    "run_gap_analysis",
    "run_scope_analysis",
    "run_test_check",
    "run_preflight",
]
