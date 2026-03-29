"""ADG Accelerator Orchestrator

Central entry point for all ADG accelerators with unified CLI.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent


def run_testing(args: list[str]) -> int:
    """Run testing accelerator."""
    cmd = [sys.executable, "-m", "tools.adg_test_accelerator"] + args
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


def run_hardening_p0(layer: str | None, dim: str | None, apply: bool) -> int:
    """Run P0 hardening."""
    cmd = [sys.executable, "tools/p0_batch_wirer.py"]
    if layer:
        cmd.extend(["--layer", layer])
    if dim:
        cmd.extend(["--dim", dim])
    if apply:
        cmd.append("--apply")
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


def run_hardening_p1(apply: bool) -> int:
    """Run P1 hardening."""
    cmd = [sys.executable, "tools/p1_batch_wire.py"]
    if apply:
        cmd.append("--apply")
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


def run_incremental_update(changed: list[str]) -> int:
    """Run incremental update."""
    cmd = [sys.executable, "tools/adg_incremental_update.py"] + changed
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


def run_fast_test(adg: bool, dry_run: bool) -> int:
    """Run fast test."""
    cmd = [sys.executable, "tools/fast_test.py"]
    if adg:
        cmd.append("--adg")
    if dry_run:
        cmd.append("--dry-run")
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode
