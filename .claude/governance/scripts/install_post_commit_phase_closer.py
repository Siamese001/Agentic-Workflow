#!/usr/bin/env python3
"""
install_post_commit_phase_closer.py — install/uninstall the phase closer as a
git post-commit hook.

The hook file lives at .git/hooks/post-commit (not tracked). This installer is
idempotent: it will replace an existing phase-closer hook but never clobber an
unrelated hook (it checks for the marker line).

Usage:
    python .claude/governance/scripts/install_post_commit_phase_closer.py
    python .claude/governance/scripts/install_post_commit_phase_closer.py --uninstall
    python .claude/governance/scripts/install_post_commit_phase_closer.py --status
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK_PATH = REPO_ROOT / ".git" / "hooks" / "post-commit"
MARKER = "# >>> post_commit_phase_closer (managed) >>>"
MARKER_END = "# <<< post_commit_phase_closer (managed) <<<"

HOOK_BLOCK = f"""{MARKER}
# Auto-close Notion Wave/Phase Convergence rows when a commit ships a phase/wave.
# Fail-open: never blocks a commit. Bypass: PHASE_CLOSER_BYPASS=1
python "$(git rev-parse --show-toplevel)/.claude/governance/scripts/post_commit_phase_closer.py" >&2 || true
{MARKER_END}
"""


def _read_hook() -> str:
    if HOOK_PATH.exists():
        return HOOK_PATH.read_text(encoding="utf-8")
    return ""


def _write_hook(content: str) -> None:
    HOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
    HOOK_PATH.write_text(content, encoding="utf-8", newline="\n")
    try:
        HOOK_PATH.chmod(0o755)
    except OSError:
        pass  # Windows — chmod is a no-op on NTFS


def _strip_managed_block(content: str) -> str:
    if MARKER not in content:
        return content
    lines = content.splitlines(keepends=True)
    out: list[str] = []
    skip = False
    for line in lines:
        if line.strip().startswith(MARKER):
            skip = True
            continue
        if skip and line.strip().startswith(MARKER_END):
            skip = False
            continue
        if not skip:
            out.append(line)
    return "".join(out)


def install() -> int:
    existing = _read_hook()
    stripped = _strip_managed_block(existing)
    if not stripped.strip():
        new = "#!/bin/sh\n" + HOOK_BLOCK
    else:
        # Preserve existing hook body; append managed block
        new = stripped.rstrip() + "\n\n" + HOOK_BLOCK
    _write_hook(new)
    print(f"Installed: {HOOK_PATH}")
    return 0


def uninstall() -> int:
    existing = _read_hook()
    if not existing:
        print("No hook file to uninstall.")
        return 0
    stripped = _strip_managed_block(existing)
    if stripped.strip() == "#!/bin/sh" or not stripped.strip():
        HOOK_PATH.unlink()
        print(f"Removed: {HOOK_PATH}")
    else:
        _write_hook(stripped)
        print(f"Stripped managed block from: {HOOK_PATH}")
    return 0


def status() -> int:
    existing = _read_hook()
    if not existing:
        print("NOT INSTALLED — no hook file")
        return 1
    installed = MARKER in existing
    print(f"Hook file: {HOOK_PATH}")
    print(f"Managed block present: {installed}")
    if not installed:
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--uninstall", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()

    # Verify we're in a git repo
    try:
        subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=REPO_ROOT,
            shell=False,
            check=True,
            capture_output=True,
            timeout=10,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
        print(f"Not a git repo or git unavailable: {exc}", file=sys.stderr)
        return 1

    if args.status:
        return status()
    if args.uninstall:
        return uninstall()
    return install()


if __name__ == "__main__":
    sys.exit(main())
