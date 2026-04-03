"""Lifecycle accelerator proxy module.

Delegates to the unified adg_lifecycle.py tool.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent


def run_generate(cache: bool = True) -> int:
    """Run full ADG generation using adg_lifecycle.py."""
    cmd = [sys.executable, "tools/adg/adg_lifecycle.py", "generate"]
    if cache:
        cmd.append("--cache")
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


def run_update(changed: list[str]) -> int:
    """Run incremental update using adg_lifecycle.py."""
    cmd = [sys.executable, "tools/adg/adg_lifecycle.py", "update", "--changed"] + changed
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


def run_sync(to_redis: bool = False, from_redis: bool = False) -> int:
    """Run Redis sync using adg_lifecycle.py."""
    cmd = [sys.executable, "tools/adg/adg_lifecycle.py", "sync"]
    if to_redis:
        cmd.append("--to-redis")
    if from_redis:
        cmd.append("--from-redis")
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


def run_status(json_output: str | None = None) -> int:
    """Run status check using adg_lifecycle.py."""
    cmd = [sys.executable, "tools/adg/adg_lifecycle.py", "status"]
    if json_output:
        cmd.extend(["--json", json_output])
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


def run_maintain(from_git: bool = False, sync_redis: bool = False) -> int:
    """Run auto-maintain using adg_lifecycle.py."""
    cmd = [sys.executable, "tools/adg/adg_lifecycle.py", "maintain"]
    if from_git:
        cmd.append("--from-git")
    if sync_redis:
        cmd.append("--sync-redis")
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


__all__ = [
    "run_generate",
    "run_update",
    "run_sync",
    "run_status",
    "run_maintain",
]
