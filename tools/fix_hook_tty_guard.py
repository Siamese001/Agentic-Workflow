"""One-shot fixer: add `sys.stdin.isatty()` guard to hook scripts that
would otherwise hang when invoked standalone.

Usage:
    python tools/fix_hook_tty_guard.py         # apply in-place
    python tools/fix_hook_tty_guard.py --dry-run  # preview only

Transformation:
    Locates `def main(` and inserts a TTY guard block as the first
    statement of main(), unless one is already present.

Idempotent: re-running is a no-op.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / ".claude" / "governance/scripts" / "_legacy_windsurf"

TARGETS = [
    "pre_write_gate.py",
    "pre_run_gate.py",
    "pre_read_gate.py",
    "pre_prompt_classifier.py",
    "pre_mcp_gate.py",
    "post_write_mcp_config_sync.py",
    "post_write_audit.py",
    "post_setup_worktree.py",
    "post_run_audit.py",
    "post_mcp_audit.py",
    "post_cursor_agent_writeback_audit.py",
    "post_cursor_agent_long_command_audit.py",
    "post_cursor_agent_author_gate_capture.py",
    "post_cursor_agent_adg_audit.py",
]

GUARD_MARKER = "sys.stdin.isatty()"

GUARD_BLOCK = """\
    # Standalone-invocation guard: avoid indefinite hang when invoked via
    # `run_command` / pwsh (inherited stdin never receives EOF). Hook path
    # pipes stdin, which is never a TTY, so hook behavior is unaffected.
    if sys.stdin.isatty():
        return 0
"""

# Regex: `def main(...)...:` followed by optional docstring. We inject
# immediately after the signature line.
MAIN_DEF_RE = re.compile(r"^(def main\([^)]*\)[^:]*:)\s*$", re.MULTILINE)


def patch_file(path: Path) -> tuple[bool, str]:
    """Return (changed, message)."""
    src = path.read_text(encoding="utf-8")
    if GUARD_MARKER in src:
        return False, "already guarded"

    match = MAIN_DEF_RE.search(src)
    if not match:
        return False, "no `def main(` found"

    insert_at = match.end()
    # Skip trailing newline after the signature.
    if insert_at < len(src) and src[insert_at] == "\n":
        insert_at += 1

    new_src = src[:insert_at] + GUARD_BLOCK + src[insert_at:]
    path.write_text(new_src, encoding="utf-8")
    return True, "patched"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not SCRIPTS_DIR.is_dir():
        print(f"FAIL: scripts dir not found: {SCRIPTS_DIR}", file=sys.stderr)
        return 1

    total_changed = 0
    total_skipped = 0
    failures = 0

    for name in TARGETS:
        path = SCRIPTS_DIR / name
        if not path.exists():
            print(f"  MISSING  {name}")
            failures += 1
            continue

        if args.dry_run:
            src = path.read_text(encoding="utf-8")
            if GUARD_MARKER in src:
                print(f"  skip     {name}  (already guarded)")
                total_skipped += 1
            elif MAIN_DEF_RE.search(src):
                print(f"  WOULD    {name}  (patch main())")
                total_changed += 1
            else:
                print(f"  SKIP     {name}  (no `def main(`)")
                total_skipped += 1
            continue

        changed, msg = patch_file(path)
        marker = "patched " if changed else "skip    "
        print(f"  {marker} {name}  ({msg})")
        if changed:
            total_changed += 1
        else:
            total_skipped += 1

    print(f"\nSummary: changed={total_changed} skipped={total_skipped} failures={failures}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
