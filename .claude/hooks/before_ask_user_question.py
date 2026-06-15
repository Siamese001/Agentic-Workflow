#!/usr/bin/env python3
"""beforeAskUserQuestion — PreToolUse relay for the native ``AskUserQuestion`` tool.

Thin relay: reads the Claude Code event JSON once, delegates the decision to
``.claude/governance/scripts/pre_ask_user_question_recommendation_gate.py`` (the testable
SSOT), and translates the gate's exit code into a Claude Code allow/block.

Self-contained on purpose — it does not depend on ``lib.claude_hook_common`` (absent in some
checkouts). Fail-open on every error so a broken gate never wedges a turn.

Contract enforced by the gate: §6 / CLAUDE.md Author-Gate — an AskUserQuestion for an
Author-Gate-class decision must mark the recommended option ``(Recommended)``, place it first,
and put numeric confidence plus Pros/Cons in every option description. A marked recommendation
with non-canonical output criteria **blocks by default** (``ASK_REC_GUARD_BYPASS=1`` overrides);
a missing recommendation stays advisory unless ``ASK_REC_GUARD_STRICT=1``.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_GATE = (
    _REPO_ROOT
    / ".claude"
    / "governance"
    / "scripts"
    / "pre_ask_user_question_recommendation_gate.py"
)
# This hook is self-contained by design (no lib.claude_hook_common import — absent in some
# checkouts), so it writes the fail-open ledger inline rather than via write_failopen_receipt.
# Schema matches lib.claude_hook_common.write_failopen_receipt so the budget gate reads both.
_FAILOPEN_RECEIPT_LOG = _REPO_ROOT / "artifacts" / "governance" / "hook_failopen_receipts.jsonl"


def _failopen_receipt(raw: str, failure_class: str, reason: str) -> None:
    """Best-effort fail-open ledger write; MUST NOT raise (would defeat fail-open)."""
    try:
        sid = ""
        try:
            parsed = json.loads(raw) if raw.strip() else {}
            if isinstance(parsed, dict):
                sid = str(parsed.get("session_id") or "")
        except (json.JSONDecodeError, ValueError):
            sid = ""
        row = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "hook": "beforeAskUserQuestion",
            "failure_class": failure_class,
            "reason": str(reason)[:500],
            "criticality": "CRITICAL_PRETOOL",
            "session_id": sid,
        }
        _FAILOPEN_RECEIPT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with _FAILOPEN_RECEIPT_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    except Exception:  # guardian: allow-broad-exception -- receipt write must never wedge a fail-open hook
        return


def main() -> int:
    try:
        raw = sys.stdin.read()
    except OSError:
        return 0  # fail-open (cannot even read stdin — nothing to record against)

    if not _GATE.is_file():
        _failopen_receipt(raw, "ask_rec_gate_script_missing", "pre_ask_user_question_recommendation_gate.py absent")
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
        _failopen_receipt(raw, "ask_rec_gate_unreachable", str(exc))
        return 0  # fail-open

    if proc.stderr:
        sys.stderr.write(proc.stderr)
    # Mirror the gate's decision: 2 == block, anything else == allow.
    return 2 if proc.returncode == 2 else 0


if __name__ == "__main__":
    raise SystemExit(main())
