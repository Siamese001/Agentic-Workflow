"""Hardening accelerator proxy module.

Delegates to the unified adg_harden.py tool.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent


def run_p0_hardening(dim: str, layer: str | None = None, apply: bool = False) -> int:
    """Run P0 hardening using adg_harden.py."""
    cmd = [sys.executable, "tools/adg/adg_harden.py", "p0", "--dim", dim]
    if layer:
        cmd.extend(["--layer", layer])
    if apply:
        cmd.append("--apply")
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


def run_p1_hardening(apply: bool = False) -> int:
    """Run P1 hardening using adg_harden.py."""
    cmd = [sys.executable, "tools/adg/adg_harden.py", "p1"]
    if apply:
        cmd.append("--apply")
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


def run_p2_hardening(apply: bool = False) -> int:
    """Run P2 hardening using adg_harden.py."""
    cmd = [sys.executable, "tools/adg/adg_harden.py", "p2"]
    if apply:
        cmd.append("--apply")
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


def run_hardening_check(all_phases: bool = False, phase: str | None = None) -> int:
    """Run hardening coverage check using adg_harden.py."""
    cmd = [sys.executable, "tools/adg/adg_harden.py", "check"]
    if all_phases:
        cmd.append("--all")
    if phase:
        cmd.extend(["--phase", phase])
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


__all__ = [
    "run_p0_hardening",
    "run_p1_hardening",
    "run_p2_hardening",
    "run_hardening_check",
]
