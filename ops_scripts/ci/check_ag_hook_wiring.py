#!/usr/bin/env python3
"""
check_ag_hook_wiring.py — CI gate: Author-Gate hook wiring invariant.

Enforces that whenever Author-Gate audit hooks are present in
post_cursor_agent_response, the pre-composition reminder hook is also wired
in pre_user_prompt with show_output=true, and that all required AG audit
hooks are visible (show_output=true).

Invariants checked:
  AG-WIRE-1: pre_user_prompt contains pre_user_prompt_author_gate_reminder.py
              with show_output=true whenever any AG audit hook is present in
              post_cursor_agent_response
  AG-WIRE-2: post_cursor_agent_author_gate_miss_detector.py must be present with
              show_output=true
  AG-WIRE-3: post_cursor_agent_author_gate_ui_audit.py must be present with
              show_output=true
  AG-WIRE-4: post_cursor_agent_ask_user_question_packet_audit.py must be present
              with show_output=true

Exit codes:
    0 = all invariants satisfied (or bypass active)
    1 = one or more violations found (fail-closed mode)
    0 = advisory mode (default): prints violations but exits 0

Bypass: AG_HOOK_WIRING_BYPASS=1 skips checks (logs bypass marker).
Fail-closed: AG_HOOK_WIRING_FAIL_CLOSED=1 makes violations exit 1.

CONSTITUTIONAL
    - No shell=True, no PowerShell
    - subprocess.run with timeout where used
    - Specific exceptions only
    - UTF-8 stdio
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOKS_PATH = REPO_ROOT / ".cursor" / "hooks.json"
VIOLATIONS_OUT = REPO_ROOT / "artifacts" / "cursor" / "ag_hook_wiring_violations.json"
CURSOR_AG_CHAIN_HOOK = REPO_ROOT / ".cursor" / "hooks" / "after_agent_author_gate_audits.py"
CURSOR_AG_CHAIN_NAME = "after_agent_author_gate_audits.py"

BYPASS_ENV = "AG_HOOK_WIRING_BYPASS"
FAIL_CLOSED_ENV = "AG_HOOK_WIRING_FAIL_CLOSED"

# Hooks that MUST be in post_cursor_agent_response with show_output=true
REQUIRED_POST_CURSOR_AGENT_HOOKS: list[dict[str, Any]] = [
    {
        "id": "AG-WIRE-2",
        "script": "post_cursor_agent_author_gate_miss_detector.py",
        "show_output": True,
        "description": "miss detector must be present and visible",
    },
    {
        "id": "AG-WIRE-3",
        "script": "post_cursor_agent_author_gate_ui_audit.py",
        "show_output": True,
        "description": "UI audit must be present and visible",
    },
    {
        "id": "AG-WIRE-4",
        "script": "post_cursor_agent_ask_user_question_packet_audit.py",
        "show_output": True,
        "description": "ask-packet audit must be present and visible",
    },
]

# Hook that MUST be in pre_user_prompt with show_output=true (AG-WIRE-1)
REQUIRED_PRE_PROMPT_HOOK = "pre_user_prompt_author_gate_reminder.py"

# Any of these in post_cursor_agent_response / afterAgentResponse triggers the wiring check
AG_AUDIT_TRIGGER_SCRIPTS = {
    "post_cursor_agent_author_gate_miss_detector.py",
    "post_cursor_agent_author_gate_ui_audit.py",
    "post_cursor_agent_author_gate_schema_audit.py",
    "post_cursor_agent_ask_user_question_packet_audit.py",
    "post_cursor_agent_author_gate_capture.py",
    "after_agent_author_gate_audits.py",
}


def _script_name(command: str) -> str:
    """Extract the script filename from a hook command string."""
    parts = command.strip().split()
    if not parts:
        return ""
    last = parts[-1]
    if last.startswith("--"):
        last = parts[-2] if len(parts) >= 2 else ""
    return Path(last).name


def _load_hooks() -> dict[str, Any]:
    try:
        return json.loads(HOOKS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"AG_HOOK_WIRING ERROR: cannot read {HOOKS_PATH}: {exc}", file=sys.stderr)
        sys.exit(2)


def _hooks_for_post_agent_response(hooks_data: dict[str, Any]) -> list[dict[str, Any]]:
    """Merge Windsurf and Cursor hook buckets that fire after the agent responds."""
    h = hooks_data.get("hooks", {})
    merged: list[dict[str, Any]] = []
    for ev in ("post_cursor_agent_response", "afterAgentResponse"):
        chunk = h.get(ev)
        if isinstance(chunk, list):
            merged.extend(chunk)
    return merged


def _hooks_for_pre_user_prompt(hooks_data: dict[str, Any]) -> list[dict[str, Any]]:
    """Merge pre-prompt hook buckets (Windsurf + Cursor beforeSubmitPrompt)."""
    h = hooks_data.get("hooks", {})
    merged: list[dict[str, Any]] = []
    for ev in ("pre_user_prompt", "beforeSubmitPrompt"):
        chunk = h.get(ev)
        if isinstance(chunk, list):
            merged.extend(chunk)
    return merged


def _cursor_ag_chain_covers(script: str, post_by_name: dict[str, dict[str, Any]]) -> bool:
    """True if the unified Cursor chain hook is wired and enumerates ``script``."""
    if CURSOR_AG_CHAIN_NAME not in post_by_name:
        return False
    try:
        text = CURSOR_AG_CHAIN_HOOK.read_text(encoding="utf-8")
    except OSError:
        return False
    return script in text


def _effective_show_output(hook: dict[str, Any], req_show: bool) -> bool:
    """Cursor hooks omit ``show_output``; treat absent as visible (passes AG-WIRE checks)."""
    if not req_show:
        return True
    if "show_output" not in hook:
        return True
    return bool(hook.get("show_output"))


def evaluate(hooks_data: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Evaluate all AG wiring invariants.
    Returns a list of violation dicts (empty = all pass).
    """
    violations: list[dict[str, Any]] = []

    post_cascade = _hooks_for_post_agent_response(hooks_data)
    pre_prompt = _hooks_for_pre_user_prompt(hooks_data)

    # Build lookup maps: script_name → hook entry
    post_by_name: dict[str, dict[str, Any]] = {}
    for h in post_cascade:
        name = _script_name(h.get("command", ""))
        if name:
            post_by_name[name] = h

    pre_by_name: dict[str, dict[str, Any]] = {}
    for h in pre_prompt:
        name = _script_name(h.get("command", ""))
        if name:
            pre_by_name[name] = h

    # Check if any AG audit trigger scripts are present at all
    ag_audit_present = any(s in post_by_name for s in AG_AUDIT_TRIGGER_SCRIPTS)

    if not ag_audit_present:
        return []

    # AG-WIRE-1: pre_user_prompt reminder hook must be present and visible
    reminder_hook = pre_by_name.get(REQUIRED_PRE_PROMPT_HOOK)
    if reminder_hook is None:
        violations.append({
            "invariant": "AG-WIRE-1",
            "severity": "ERROR",
            "message": (
                f"pre_prompt hook chain does not contain {REQUIRED_PRE_PROMPT_HOOK}. "
                "AG audit hooks are wired but the pre-composition reminder is missing. "
                "Add pre_user_prompt_author_gate_reminder.py to beforeSubmitPrompt (or pre_user_prompt)."
            ),
        })
    elif not _effective_show_output(reminder_hook, True):
        violations.append({
            "invariant": "AG-WIRE-1",
            "severity": "ERROR",
            "message": (
                f"{REQUIRED_PRE_PROMPT_HOOK} is present in pre_user_prompt but "
                "show_output=false. Pipeline reminders will be invisible. "
                "Set show_output=true."
            ),
        })

    # AG-WIRE-2/3/4: required post-response audit hooks must be present and visible
    # (or satisfied by ``after_agent_author_gate_audits.py`` chain that enumerates them).
    for req in REQUIRED_POST_CURSOR_AGENT_HOOKS:
        script = req["script"]
        inv_id = req["id"]
        hook = post_by_name.get(script)
        chain_ok = hook is None and _cursor_ag_chain_covers(script, post_by_name)
        if hook is None and not chain_ok:
            violations.append({
                "invariant": inv_id,
                "severity": "ERROR",
                "message": (
                    f"post-response hooks do not contain {script} "
                    f"and `.cursor/hooks/after_agent_author_gate_audits.py` does not cover it. "
                    f"{req['description']}."
                ),
            })
            continue
        if chain_ok:
            continue
        if req["show_output"] and not _effective_show_output(hook, True):
            violations.append({
                "invariant": inv_id,
                "severity": "ERROR",
                "message": (
                    f"{script} is present in post-response hooks but "
                    f"show_output=false — violations may be invisible. "
                    f"Set show_output=true. ({req['description']})"
                ),
            })

    return violations


def _write_report(violations: list[dict[str, Any]]) -> None:
    try:
        VIOLATIONS_OUT.parent.mkdir(parents=True, exist_ok=True)
        report = {"total_violations": len(violations), "violations": violations}
        VIOLATIONS_OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    except OSError as exc:
        print(f"AG_HOOK_WIRING WARNING: could not write report: {exc}", file=sys.stderr)


def main() -> int:
    if os.environ.get(BYPASS_ENV):
        print(
            f"AG_HOOK_WIRING BYPASS: {BYPASS_ENV}=1 — skipping wiring checks",
            file=sys.stderr,
        )
        _write_report([])
        return 0

    if not HOOKS_PATH.exists():
        print(
            f"AG_HOOK_WIRING ERROR: {HOOKS_PATH} not found",
            file=sys.stderr,
        )
        return 2

    hooks_data = _load_hooks()
    violations = evaluate(hooks_data)
    _write_report(violations)

    fail_closed = bool(os.environ.get(FAIL_CLOSED_ENV))

    if not violations:
        print("AG_HOOK_WIRING: all invariants satisfied (AG-WIRE-1 through AG-WIRE-4)")
        return 0

    print(f"AG_HOOK_WIRING: {len(violations)} violation(s) found:")
    for v in violations:
        prefix = "ERROR" if v["severity"] == "ERROR" else "WARN"
        print(f"  [{prefix}] [{v['invariant']}] {v['message']}")

    if fail_closed:
        print(
            f"\nAG_HOOK_WIRING FAIL-CLOSED ({FAIL_CLOSED_ENV}=1): exiting 1",
            file=sys.stderr,
        )
        return 1

    print(
        f"\nAG_HOOK_WIRING ADVISORY: violations logged to {VIOLATIONS_OUT}. "
        f"Set {FAIL_CLOSED_ENV}=1 to make this gate fail-closed.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
