#!/usr/bin/env python3
"""beforeAskUserQuestion — PreToolUse relay for the native ``AskUserQuestion`` tool.

Thin relay: reads the Claude Code event JSON once, delegates the decision to
``.claude/governance/scripts/pre_ask_user_question_recommendation_gate.py`` (the testable
SSOT), and translates the gate's exit code into a Claude Code allow/block.

Self-contained on purpose — it does not depend on ``lib.claude_hook_common`` (absent in some
checkouts). Fail-open on every error so a broken gate never wedges a turn.

Contract enforced by the gate: §6 / CLAUDE.md Author-Gate — an AskUserQuestion for an
Author-Gate-class decision must mark the recommended option ``(Recommended)`` and carry a
confidence signal. A marked recommendation with NO confidence signal **blocks by default**
(``ASK_REC_GUARD_BYPASS=1`` overrides); a missing/last recommendation stays advisory unless
``ASK_REC_GUARD_STRICT=1``.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_GATE = (
    _REPO_ROOT
    / ".claude"
    / "governance"
    / "scripts"
    / "pre_ask_user_question_recommendation_gate.py"
)


def main() -> int:
    try:
        raw = sys.stdin.read()
    except OSError:
        return 0  # fail-open

    if not _GATE.is_file():
        return 0  # gate missing — fail-open

    try:
        proc = subprocess.run(
            [sys.executable, str(_GATE)],
            input=raw,
            cwd=str(_REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
            env={**os.environ, "PYTHONPATH": str(_REPO_ROOT)},
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        sys.stderr.write(f"before_ask_user_question: gate unreachable ({exc}) — allowing\n")
        return 0  # fail-open

    if proc.stderr:
        sys.stderr.write(proc.stderr)
    # Mirror the gate's decision: 2 == block, anything else == allow.
    return 2 if proc.returncode == 2 else 0


if __name__ == "__main__":
    raise SystemExit(main())
