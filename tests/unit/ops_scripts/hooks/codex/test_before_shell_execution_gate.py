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
HOOK = REPO_ROOT / ".codex" / "hooks" / "before_shell_execution.py"
GATE = REPO_ROOT / ".codex" / "governance" / "scripts" / "pre_run_gate.py"


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


def test_hook_blocks_direct_gh_pr_merge_without_closeout_chain():
    proc = _run_hook("gh pr merge 123 --merge")

    assert proc.returncode == 2
    assert "codex_main_closeout.py --apply --fetch --json --publication-only" in proc.stdout


def test_hook_blocks_direct_push_to_main_without_closeout_chain():
    proc = _run_hook("git push origin HEAD:refs/heads/main")

    assert proc.returncode == 2
    assert "PR/main completion commands must chain publication closeout proof" in proc.stdout


def test_hook_blocks_pr_merge_with_legacy_strict_only_closeout_chain():
    proc = _run_hook(
        "gh pr merge 123 --merge && "
        "git switch main && "
        "python scripts/governance/codex_main_closeout.py --apply --fetch --json && "
        "python scripts/governance/codex_main_closeout.py --check --fetch --json"
    )

    assert proc.returncode == 2


def test_hook_allows_pr_merge_when_publication_closeout_is_chained():
    proc = _run_hook(
        "gh pr merge 123 --merge && "
        "git switch main && "
        "python scripts/governance/codex_main_closeout.py --apply --fetch --json --publication-only && "
        "python scripts/governance/codex_main_closeout.py --check --fetch --json --publication-only"
    )

    assert proc.returncode == 0


def test_hook_allows_feature_branch_push_without_closeout_chain():
    proc = _run_hook("git push origin HEAD:refs/heads/codex/feature")

    assert proc.returncode == 0


def test_hook_allows_read_only_pr_commands_without_closeout_chain():
    for command in ("gh pr list --state open", "gh pr view 123", "gh pr checks 123"):
        proc = _run_hook(command)
        assert proc.returncode == 0


def test_hook_allows_slash_namespace_worktree_branch_creation():
    proc = _run_hook(
        "git worktree add C:/Git/Agentic-Workflow-FRESH-worktrees/zen-mcnulty-654733 "
        "-b claude/zen-mcnulty-654733 origin/main"
    )

    assert proc.returncode == 0


def test_hook_allows_generated_low_signal_worktree_branch_creation():
    proc = _run_hook(
        "git worktree add C:/Git/Agentic-Workflow-FRESH-worktrees/claude-zen-mcnulty-654733 "
        "-b claude-zen-mcnulty-654733 origin/main"
    )

    assert proc.returncode == 0


def test_hook_allows_worktree_folder_branch_mismatch():
    proc = _run_hook(
        "git worktree add C:/Git/Agentic-Workflow-FRESH-worktrees/zen-mcnulty-654733 "
        "-b claude-worktree-creation-guard origin/main"
    )

    assert proc.returncode == 0


def test_hook_allows_app_worktree_branch_named_for_single_wave():
    proc = _run_hook(
        "git worktree add C:/Git/Agentic-Workflow-FRESH-worktrees/claude-apps-rg-wave4-tests "
        "-b claude-apps-rg-wave4-tests origin/main"
    )

    assert proc.returncode == 0


def test_hook_allows_checkout_branch_creation_with_slash_namespace():
    proc = _run_hook("git checkout -b claude/zen-mcnulty-654733 origin/main")

    assert proc.returncode == 0


def test_hook_allows_branch_rename_to_generated_name():
    proc = _run_hook("git branch -m claude-zen-mcnulty-654733")

    assert proc.returncode == 0


def test_hook_allows_canonical_worktree_branch_creation():
    proc = _run_hook(
        "git worktree add C:/Git/Agentic-Workflow-FRESH-worktrees/claude-worktree-creation-guard "
        "-b claude-worktree-creation-guard origin/main"
    )

    assert proc.returncode == 0


def test_hook_blocks_worktree_creation_outside_ssot_root():
    proc = _run_hook(
        "git worktree add C:/Users/amita/.codex/worktrees/claude-worktree-creation-guard "
        "-b claude-worktree-creation-guard origin/main"
    )

    assert proc.returncode == 2
    assert "Agentic-Workflow worktree SSOT root" in proc.stdout
    assert "Agentic-Workflow-FRESH-worktrees" in proc.stdout


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


def test_hook_does_not_police_branch_owner_for_shell_creation():
    proc = _run_hook(
        "git switch -c claude-worktree-creation-guard origin/main",
        env={"WORKTREE_IDE_OWNER": "codex"},
    )

    assert proc.returncode == 0
