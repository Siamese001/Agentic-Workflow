"""ADG Accelerator Orchestrator

Central entry point for all ADG accelerators with unified CLI.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent


def run_testing(args: list[str]) -> int:
    """Run testing accelerator using new adg_test.py tool."""
    cmd = [sys.executable, "tools/adg/adg_test.py"] + args
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


def run_hardening_p0(layer: str | None, dim: str | None, apply: bool) -> int:
    """Run P0 hardening using new adg_harden.py tool."""
    cmd = [sys.executable, "tools/adg/adg_harden.py", "p0"]
    if layer:
        cmd.extend(["--layer", layer])
    if dim:
        cmd.extend(["--dim", dim])
    if apply:
        cmd.append("--apply")
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


def run_hardening_p1(apply: bool) -> int:
    """Run P1 hardening using new adg_harden.py tool."""
    cmd = [sys.executable, "tools/adg/adg_harden.py", "p1"]
    if apply:
        cmd.append("--apply")
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


def run_hardening_p2(apply: bool) -> int:
    """Run P2 hardening using new adg_harden.py tool."""
    cmd = [sys.executable, "tools/adg/adg_harden.py", "p2"]
    if apply:
        cmd.append("--apply")
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


def run_incremental_update(changed: list[str]) -> int:
    """Run incremental update using new adg_lifecycle.py tool."""
    cmd = [sys.executable, "tools/adg/adg_lifecycle.py", "update", "--changed"] + changed
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


def run_fast_test(adg: bool, dry_run: bool) -> int:
    """Run fast test using new adg_test.py tool."""
    cmd = [sys.executable, "tools/adg/adg_test.py", "run"]
    if adg:
        cmd.append("--adg-scope")
    if dry_run:
        cmd.append("--dry-run")
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode
