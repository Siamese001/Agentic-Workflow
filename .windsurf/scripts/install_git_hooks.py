#!/usr/bin/env python3
"""
install_git_hooks.py — Opt-in installer for Windsurf-managed git hooks.

Currently installs:
    - post-commit: invokes .windsurf/scripts/post_commit_outcome_binder.py --head

Idempotent: re-running refreshes the hook to latest content.

Usage:
    python .windsurf/scripts/install_git_hooks.py           # install
    python .windsurf/scripts/install_git_hooks.py --check   # verify installed
    python .windsurf/scripts/install_git_hooks.py --uninstall

Exit codes:
    0 = success / already installed / uninstalled
    1 = check failed (missing or outdated)
    2 = fatal error (no .git dir, permission denied, etc.)

CONSTITUTIONAL
    - No PowerShell; uses python shebang via sys.executable
    - UTF-8 explicit on all file ops
    - Catches OSError specifically (no bare except)
"""

from __future__ import annotations

import argparse
import os
import stat
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GIT_DIR = REPO_ROOT / ".git"
HOOKS_DIR = GIT_DIR / "hooks"
HOOK_NAME = "post-commit"
HOOK_PATH = HOOKS_DIR / HOOK_NAME

# Sentinel so we can detect our managed hook vs. a user's custom one.
MARKER = "# WINDSURF-MANAGED-HOOK: post-commit-outcome-binder"

HOOK_CONTENT = f"""#!/usr/bin/env bash
{MARKER}
# Installed by .windsurf/scripts/install_git_hooks.py
# Purpose: bind executed decisions to their commit outcomes (harness HITL W2)
# Runs in background; failures are non-blocking (exit 0 always to not block commits)

set +e
python .windsurf/scripts/post_commit_outcome_binder.py --head >/dev/null 2>&1 &
disown 2>/dev/null || true
exit 0
"""


def _verify_git_repo() -> int:
    if not GIT_DIR.is_dir():
        print(f"[install_git_hooks] No .git directory at {GIT_DIR}", file=sys.stderr)
        return 2
    try:
        HOOKS_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"[install_git_hooks] Cannot create hooks dir: {exc}", file=sys.stderr)
        return 2
    return 0


def install() -> int:
    rc = _verify_git_repo()
    if rc != 0:
        return rc

    # Preserve non-managed hooks: if a hook exists and lacks our MARKER,
    # append ours as a wrapper rather than overwrite.
    existing = ""
    if HOOK_PATH.exists():
        try:
            existing = HOOK_PATH.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"[install_git_hooks] Cannot read existing hook: {exc}", file=sys.stderr)
            return 2

    if MARKER in existing:
        # Managed hook already installed; refresh content.
        final_content = HOOK_CONTENT
        action = "refreshed"
    elif existing.strip():
        # Foreign hook present — prepend our block, keep their logic.
        final_content = HOOK_CONTENT.rstrip() + "\n\n# ---- existing hook preserved below ----\n" + existing
        action = "wrapped (preserved existing)"
    else:
        final_content = HOOK_CONTENT
        action = "installed"

    try:
        HOOK_PATH.write_text(final_content, encoding="utf-8", newline="\n")
        # Make executable (owner + group + other)
        mode = HOOK_PATH.stat().st_mode
        HOOK_PATH.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except OSError as exc:
        print(f"[install_git_hooks] Write failed: {exc}", file=sys.stderr)
        return 2

    print(f"[install_git_hooks] post-commit {action} at {HOOK_PATH}")
    print("  Validate: git commit --allow-empty -m 'test hook'")
    return 0


def check() -> int:
    rc = _verify_git_repo()
    if rc != 0:
        return rc
    if not HOOK_PATH.exists():
        print(f"[install_git_hooks] NOT INSTALLED: {HOOK_PATH}")
        return 1
    try:
        content = HOOK_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"[install_git_hooks] Cannot read hook: {exc}", file=sys.stderr)
        return 2
    if MARKER not in content:
        print(f"[install_git_hooks] STALE/FOREIGN: {HOOK_PATH} (marker missing)")
        return 1
    print(f"[install_git_hooks] OK: managed hook present at {HOOK_PATH}")
    return 0


def uninstall() -> int:
    if not HOOK_PATH.exists():
        print("[install_git_hooks] No hook to uninstall.")
        return 0
    try:
        content = HOOK_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"[install_git_hooks] Cannot read hook: {exc}", file=sys.stderr)
        return 2
    if MARKER not in content:
        print("[install_git_hooks] Foreign hook present (not managed); refusing to delete.")
        print(f"  Manual action required: {HOOK_PATH}")
        return 1
    # Strip our block
    parts = content.split(MARKER, 1)
    if len(parts) == 2:
        # Find the separator we added when wrapping
        sep = "# ---- existing hook preserved below ----"
        if sep in parts[1]:
            preserved = parts[1].split(sep, 1)[1].lstrip("\n")
            try:
                HOOK_PATH.write_text(preserved, encoding="utf-8", newline="\n")
                print(f"[install_git_hooks] Restored pre-existing hook at {HOOK_PATH}")
            except OSError as exc:
                print(f"[install_git_hooks] Restore failed: {exc}", file=sys.stderr)
                return 2
        else:
            try:
                HOOK_PATH.unlink()
                print(f"[install_git_hooks] Removed managed hook at {HOOK_PATH}")
            except OSError as exc:
                print(f"[install_git_hooks] Unlink failed: {exc}", file=sys.stderr)
                return 2
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Install/verify Windsurf git hooks.")
    parser.add_argument("--check", action="store_true", help="Verify hook is installed")
    parser.add_argument("--uninstall", action="store_true", help="Remove managed hook")
    args = parser.parse_args()
    if args.check:
        return check()
    if args.uninstall:
        return uninstall()
    return install()


if __name__ == "__main__":
    sys.exit(main())
