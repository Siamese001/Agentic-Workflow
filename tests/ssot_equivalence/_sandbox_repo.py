"""Sandbox repo creator for hermetic legacy execution testing.

Provides isolated repo copies (via git worktree or local clone) so that
legacy execute_ssot can run with full write permissions without affecting
the primary working tree.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path

from tests._helpers.robust_fs import robust_rmtree, robust_subprocess_run

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "_sandbox_repo")
_emit_applies_guardrail("p0", "_sandbox_repo", "p0_governance")
_emit_reads_policy_state("p0", "_sandbox_repo", "policy_binding")
_emit_snapshots_state("p0", "_sandbox_repo", "state_snapshot")
emit_replay_key("p0", "_sandbox_repo")
emit_determinism_digest("p0", "_sandbox_repo")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# ── Configuration constants ────────────────────────────────────────
MAX_CAPTURE: int = 2000
DEFAULT_TIMEOUT: int = 120
GIT_PROBE_TIMEOUT: int = 10
WORKTREE_TIMEOUT: int = 60
CLONE_TIMEOUT: int = 120
CLEANUP_TIMEOUT: int = 30
PRUNE_TIMEOUT: int = 10
LEGACY_RUN_TIMEOUT: int = 120


def run_cmd(
    cwd: Path,
    cmd: list[str],
    timeout: int = DEFAULT_TIMEOUT,
    env: dict[str, str] | None = None,
) -> tuple[int, str, str]:
    """Run a command and return ``(returncode, stdout_head, stderr_head)``."""
    merged_env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", **(env or {})}
    try:
        result = robust_subprocess_run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(cwd),
            timeout=timeout,
            env=merged_env,
        )
        return (
            result.returncode,
            result.stdout[:MAX_CAPTURE],
            result.stderr[:MAX_CAPTURE],
        )
    except subprocess.TimeoutExpired:
        return (-1, "", f"Command timed out after {timeout}s")
    except FileNotFoundError:
        return (-2, "", f"Command not found: {cmd[0]}")


def _git_available(repo_root: Path) -> bool:
    """Return True if git is callable from *repo_root*."""
    rc, _, _ = run_cmd(repo_root, ["git", "--version"], timeout=GIT_PROBE_TIMEOUT)
    return rc == 0


def _sandbox_dir_name(node_id: str = "") -> str:
    """Derive a deterministic unique directory name from *node_id*.

    Uses sha256 truncated to 16 hex chars so parallel tests never
    collide on the same worktree path (fixes WinError 183).
    """
    tag = node_id or "default"
    return "ssot_sandbox_" + hashlib.sha256(tag.encode()).hexdigest()[:16]


def create_sandbox(
    repo_root: Path,
    sandbox_root: Path,
    node_id: str = "",
) -> Path:
    """Create an isolated sandbox of *repo_root* under *sandbox_root*.

    Tries strategies in order:
      A) ``git worktree add --detach`` (fastest, shares objects)
      B) ``git clone --local`` (independent, hardlinked objects)

    *node_id* is used to derive a unique sandbox directory name so that
    parallel fixtures never collide (§Wave5.0.6).

    Returns the sandbox repo path.
    Raises ``RuntimeError`` if all strategies fail.
    """
    sandbox_path = sandbox_root / _sandbox_dir_name(node_id)

    # Strategy A: git worktree (fastest)
    rc, _, err_a = run_cmd(
        repo_root,
        ["git", "worktree", "add", "--detach", str(sandbox_path)],
        timeout=WORKTREE_TIMEOUT,
    )
    if rc == 0:
        return sandbox_path

    # Strategy B: local clone (independent)
    rc, _, err_b = run_cmd(
        repo_root,
        ["git", "clone", "--local", str(repo_root), str(sandbox_path)],
        timeout=CLONE_TIMEOUT,
    )
    if rc == 0:
        return sandbox_path

    raise RuntimeError(f"Cannot create sandbox.\n  worktree error: {err_a}\n  clone error: {err_b}")


def destroy_sandbox(repo_root: Path, sandbox_path: Path) -> None:
    """Remove sandbox, best-effort.  Never raises."""
    try:
        # Try git worktree remove first (handles worktree strategy)
        run_cmd(
            repo_root,
            ["git", "worktree", "remove", "--force", str(sandbox_path)],
            timeout=CLEANUP_TIMEOUT,
        )
        # Prune stale worktree refs
        run_cmd(repo_root, ["git", "worktree", "prune"], timeout=PRUNE_TIMEOUT)
    except (subprocess.CalledProcessError, OSError):
        pass

    # Force-remove directory if still present
    robust_rmtree(sandbox_path)


def run_legacy_in_sandbox(
    sandbox_path: Path,
    extra_args: list[str] | None = None,
    timeout: int = LEGACY_RUN_TIMEOUT,
) -> dict:
    """Run legacy entrypoint inside the sandbox and return capture dict.

    Returns dict with keys: command, returncode, stdout_head, stderr_head.
    """
    cmd = [
        sys.executable,
        "-m",
        "agentic_core.L0_routing.scripts.execute_ssot_entrypoint",
        "--legacy",
        *(extra_args or []),
    ]
    env_overrides = {
        "PYTHONDONTWRITEBYTECODE": "1",
        "V15_ENFORCEMENT": "0",
    }
    rc, stdout, stderr = run_cmd(
        sandbox_path,
        cmd,
        timeout=timeout,
        env=env_overrides,
    )
    return {
        "command": cmd,
        "returncode": rc,
        "stdout_head": stdout,
        "stderr_head": stderr,
    }
