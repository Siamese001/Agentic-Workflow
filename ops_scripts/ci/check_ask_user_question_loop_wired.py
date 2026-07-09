#!/usr/bin/env python3
"""check_ask_user_question_loop_wired.py — verify the Codex request_user_input loop is wired.

Plan: askq-confidence-meta-learning-loop-c4e7a1 (W3.1).

The loop only learns if the Codex request_user_input seams are connected:
  1. SHAPE — a ``PreToolUse`` hook on ``request_user_input``
     is registered in ``.codex/hooks.json`` and points at ``before_ask_user_question.py``.
  2. CAPTURE — a ``PostToolUse`` hook on that Codex tool name is registered
     and points at ``after_ask_user_question.py``.
  3. The capture SSOT (``post_ask_user_question_capture.py``) and the calibration helper
     (``tools/ledgers/ask_user_question_calibration.py``) exist on disk.
  4. WRITABLE — the ``ask_user_question_decisions`` ledger can be opened/created.

A regression on any of these silently re-opens the loop (decisions stop being recorded and
confidence stops being calibrated), which no test would otherwise catch. This gate makes that
visible.

Advisory by default (exits 0, prints PASS/FAIL). Set ``ASKQ_LOOP_WIRED_FAIL_CLOSED=1`` to exit 1
on any failure (recommended for the consolidated CI job once the hook has shipped to main).

Run manually:
  python ops_scripts/ci/check_ask_user_question_loop_wired.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SETTINGS = ROOT / ".codex" / "hooks.json"
SHAPE_HOOK = ROOT / ".codex" / "hooks" / "before_ask_user_question.py"
CAPTURE_HOOK = ROOT / ".codex" / "hooks" / "after_ask_user_question.py"
CAPTURE_SSOT = ROOT / ".codex" / "governance" / "scripts" / "post_ask_user_question_capture.py"
CALIB_HELPER = ROOT / "tools" / "ledgers" / "ask_user_question_calibration.py"
QUESTION_TOOL_MATCH_TOKENS = ("request_user_input",)


def _fail_closed() -> bool:
    return os.environ.get("ASKQ_LOOP_WIRED_FAIL_CLOSED", "").strip().lower() in ("1", "true", "yes")


def _hook_registered(stage: str, hook_name: str) -> bool:
    """True when hooks.json has a stage matcher covering Codex request_user_input."""
    try:
        data = json.loads(SETTINGS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    for block in data.get("hooks", {}).get(stage, []):
        if not isinstance(block, dict):
            continue
        matcher = str(block.get("matcher") or "")
        if not all(token in matcher for token in QUESTION_TOOL_MATCH_TOKENS):
            continue
        for hook in block.get("hooks", []):
            if isinstance(hook, dict) and hook_name in str(hook.get("command", "")):
                return True
    return False


def _pre_hook_registered() -> bool:
    """True when PreToolUse covers native question-tool shape enforcement."""
    return _hook_registered("PreToolUse", "before_ask_user_question.py")


def _post_hook_registered() -> bool:
    """True when PostToolUse covers native question-tool decision capture."""
    return _hook_registered("PostToolUse", "after_ask_user_question.py")


def _ledger_writable() -> bool:
    """True when the ask_user_question ledger's directory is writable.

    Probes the parent directory with a temp file rather than opening the ledger itself — a
    health check must not materialize the real ledger as a side effect (that would corrupt
    tests/tools that assume an absent ledger).
    """
    try:
        from tools.ledgers.ask_user_question_ledger import LEDGER_PATH

        parent = LEDGER_PATH.parent
        parent.mkdir(parents=True, exist_ok=True)
        probe = parent / ".loop_wired_probe.tmp"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return True
    except Exception:  # guardian: allow-broad-exception -- any failure means "not writable"
        return False


def run_checks() -> list[tuple[str, bool, str]]:
    """Return [(name, ok, detail)] for each loop seam."""
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    return [
        ("pre_tool_use_hook_registered", _pre_hook_registered(),
         "hooks.json PreToolUse matcher covers request_user_input -> before_ask_user_question.py"),
        ("post_tool_use_hook_registered", _post_hook_registered(),
         "hooks.json PostToolUse matcher covers request_user_input -> after_ask_user_question.py"),
        ("shape_hook_exists", SHAPE_HOOK.is_file(), str(SHAPE_HOOK.relative_to(ROOT))),
        ("capture_hook_exists", CAPTURE_HOOK.is_file(), str(CAPTURE_HOOK.relative_to(ROOT))),
        ("capture_ssot_exists", CAPTURE_SSOT.is_file(), str(CAPTURE_SSOT.relative_to(ROOT))),
        ("calibration_helper_exists", CALIB_HELPER.is_file(), str(CALIB_HELPER.relative_to(ROOT))),
        ("ledger_writable", _ledger_writable(), "ask_user_question_decisions ledger create/write"),
    ]


def main() -> int:
    results = run_checks()
    failures = [r for r in results if not r[1]]
    for name, ok, detail in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name} — {detail}")
    if failures:
        print(
            f"\n[check_ask_user_question_loop_wired] FAIL — {len(failures)} seam(s) not wired "
            "(the meta-learning loop is open). See plan askq-confidence-meta-learning-loop-c4e7a1."
        )
        return 1 if _fail_closed() else 0
    print("\n[check_ask_user_question_loop_wired] PASS — capture + consult loop is wired.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
