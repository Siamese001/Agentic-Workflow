#!/usr/bin/env python3
"""afterAskUserQuestion — PostToolUse relay for native question tools.

Thin relay: reads the Claude Code event JSON once and delegates to
``.codex/governance/scripts/post_ask_user_question_capture.py`` (the testable SSOT), which
records the decision (options + confidence + the user's selection) to the
``ask_user_question_decisions`` ledger — closing the WRITE+SELECTION seam of the
AskUserQuestion confidence meta-learning loop (plan askq-confidence-meta-learning-loop-c4e7a1).

Self-contained on purpose — no dependency on ``lib.codex_hook_common``. PostToolUse never
blocks, so this ALWAYS exits 0; any error is swallowed (capture must never wedge a turn).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = (
    _REPO_ROOT
    / ".codex"
    / "governance"
    / "scripts"
    / "post_ask_user_question_capture.py"
)


def main() -> int:
    try:
        raw = sys.stdin.read()
    except OSError:
        return 0
    if not _SCRIPT.is_file():
        return 0
    try:
        proc = subprocess.run(
            [sys.executable, str(_SCRIPT)],
            input=raw,
            cwd=str(_REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
            env={**os.environ, "PYTHONPATH": str(_REPO_ROOT)},
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        sys.stderr.write(f"after_ask_user_question: capture unreachable ({exc}) — ignoring\n")
        return 0
    if proc.stderr:
        sys.stderr.write(proc.stderr)
    return 0  # PostToolUse: never block


if __name__ == "__main__":
    raise SystemExit(main())
