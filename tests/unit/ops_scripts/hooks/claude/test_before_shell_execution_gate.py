"""before_shell_execution.py now ENFORCES the turn-hanging command guards.

Reconciliation of the governance backend (plan always-on-rule-surface-cut-c7f3a1): the
`python -c` quote-hazard ban and the interactive/pager ban (constitutional §26 +
python-dash-c-quote-hazard.md) were implemented in pre_run_gate.py but that script was never
dispatched — so the bans were DOCTRINE-ONLY. The live PreToolUse Bash hook now imports
``pre_run_gate.shell_command_block_reason`` and blocks. These tests pin that wiring.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
HOOK = REPO_ROOT / ".claude" / "hooks" / "before_shell_execution.py"
GATE = REPO_ROOT / ".claude" / "governance" / "scripts" / "pre_run_gate.py"


def _gate_module():
    spec = importlib.util.spec_from_file_location("_pre_run_gate_under_test", GATE)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- unit: the reason helper that the hook calls ---------------------------------------

def test_reason_flags_piped_pager():
    assert _gate_module().shell_command_block_reason("cat big.json | less")


def test_reason_flags_leading_pager():
    assert _gate_module().shell_command_block_reason("more output.txt")


def test_reason_flags_quote_hazard():
    # actual command: python -c "print(\"hi\")"  — escaped double-quote in the -c body
    assert _gate_module().shell_command_block_reason('python -c "print(\\"hi\\")"')


def test_reason_allows_safe_commands():
    g = _gate_module()
    assert g.shell_command_block_reason("git status") is None
    assert g.shell_command_block_reason("python tmp.py") is None
    assert g.shell_command_block_reason("rg -n pattern src/") is None


# --- e2e: the live hook blocks/allows via subprocess (stdin JSON payload) --------------

def _run_hook(command: str, *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    payload = {"tool_name": "Bash", "tool_input": {"command": command}}
    run_env = os.environ.copy()
    if env:
        run_env.update(env)
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=run_env,
        timeout=30,
    )


def test_hook_blocks_interactive_pager():
    proc = _run_hook("cat big.json | less")
    assert proc.returncode == 2
    assert "block" in proc.stdout.lower()


def test_hook_allows_safe_command():
    proc = _run_hook("git status")
    assert proc.returncode == 0


def test_hook_blocks_slash_namespace_worktree_branch():
    proc = _run_hook(
        "git worktree add C:/Git/Agentic-Workflow-FRESH-worktrees/zen-mcnulty-654733 "
        "-b claude/zen-mcnulty-654733 origin/main"
    )

    assert proc.returncode == 2
    assert "branch must not contain slash path separators" in proc.stdout
    assert "branch must start with `claude-`" in proc.stdout


def test_hook_blocks_generated_low_signal_worktree_branch():
    proc = _run_hook(
        "git worktree add C:/Git/Agentic-Workflow-FRESH-worktrees/claude-zen-mcnulty-654733 "
        "-b claude-zen-mcnulty-654733 origin/main"
    )

    assert proc.returncode == 2
    assert "high-signal" in proc.stdout


def test_hook_blocks_worktree_folder_branch_mismatch():
    proc = _run_hook(
        "git worktree add C:/Git/Agentic-Workflow-FRESH-worktrees/zen-mcnulty-654733 "
        "-b claude-worktree-creation-guard origin/main"
    )

    assert proc.returncode == 2
    assert "worktree folder basename must exactly equal the local branch name" in proc.stdout


def test_hook_blocks_app_worktree_branch_named_for_single_wave():
    proc = _run_hook(
        "git worktree add C:/Git/Agentic-Workflow-FRESH-worktrees/claude-apps-rg-wave4-tests "
        "-b claude-apps-rg-wave4-tests origin/main"
    )

    assert proc.returncode == 2
    assert "not a wave-specific slice" in proc.stdout
    assert "claude-apps-rg-hotspot-tests" in proc.stdout


def test_hook_blocks_checkout_branch_creation_with_slash_namespace():
    proc = _run_hook("git checkout -b claude/zen-mcnulty-654733 origin/main")

    assert proc.returncode == 2
    assert "branch must not contain slash path separators" in proc.stdout


def test_hook_blocks_branch_rename_to_generated_name():
    proc = _run_hook("git branch -m claude-zen-mcnulty-654733")

    assert proc.returncode == 2
    assert "high-signal" in proc.stdout


def test_hook_allows_canonical_worktree_branch_creation():
    proc = _run_hook(
        "git worktree add C:/Git/Agentic-Workflow-FRESH-worktrees/claude-worktree-creation-guard "
        "-b claude-worktree-creation-guard origin/main"
    )

    assert proc.returncode == 0


def test_hook_allows_detached_publish_worktree():
    proc = _run_hook(
        "git worktree add --detach "
        "C:/Git/Agentic-Workflow-FRESH-worktrees/codex-main-publish-worktree origin/main"
    )

    assert proc.returncode == 0


def test_hook_allows_non_creation_branch_metadata_command():
    proc = _run_hook("git branch --set-upstream-to origin/main claude/zen-mcnulty-654733")

    assert proc.returncode == 0


def test_hook_allows_canonical_branch_track_creation():
    proc = _run_hook("git branch --track claude-worktree-creation-guard origin/main")

    assert proc.returncode == 0


def test_hook_respects_codex_owner_for_branch_creation():
    proc = _run_hook(
        "git switch -c claude-worktree-creation-guard origin/main",
        env={"WORKTREE_IDE_OWNER": "codex"},
    )

    assert proc.returncode == 2
    assert "branch must start with `codex-`" in proc.stdout
