#!/usr/bin/env python3
"""
check_ag_hook_wiring.py — CI gate: Author-Gate hook wiring invariant.

Enforces that whenever Author-Gate audit hooks are present in
post_cascade_response, the pre-composition reminder hook is also wired
in pre_user_prompt with show_output=true, and that all required AG audit
hooks are visible (show_output=true).

Invariants checked:
  AG-WIRE-1: pre_user_prompt contains pre_user_prompt_author_gate_reminder.py
              with show_output=true whenever any AG audit hook is present in
              post_cascade_response
  AG-WIRE-2: post_cascade_author_gate_miss_detector.py must be present with
              show_output=true
  AG-WIRE-3: post_cascade_author_gate_ui_audit.py must be present with
              show_output=true
  AG-WIRE-4: post_cascade_ask_user_question_packet_audit.py must be present
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
HOOKS_PATH = REPO_ROOT / ".windsurf" / "hooks.json"
VIOLATIONS_OUT = REPO_ROOT / "artifacts" / "windsurf" / "ag_hook_wiring_violations.json"

BYPASS_ENV = "AG_HOOK_WIRING_BYPASS"
FAIL_CLOSED_ENV = "AG_HOOK_WIRING_FAIL_CLOSED"

# Hooks that MUST be in post_cascade_response with show_output=true
REQUIRED_POST_CASCADE_HOOKS: list[dict[str, Any]] = [
    {
        "id": "AG-WIRE-2",
        "script": "post_cascade_author_gate_miss_detector.py",
        "show_output": True,
        "description": "miss detector must be present and visible",
    },
    {
        "id": "AG-WIRE-3",
        "script": "post_cascade_author_gate_ui_audit.py",
        "show_output": True,
        "description": "UI audit must be present and visible",
    },
    {
        "id": "AG-WIRE-4",
        "script": "post_cascade_ask_user_question_packet_audit.py",
        "show_output": True,
        "description": "ask-packet audit must be present and visible",
    },
]

# Hook that MUST be in pre_user_prompt with show_output=true (AG-WIRE-1)
REQUIRED_PRE_PROMPT_HOOK = "pre_user_prompt_author_gate_reminder.py"

# Any of these in post_cascade_response triggers the wiring check
AG_AUDIT_TRIGGER_SCRIPTS = {
    "post_cascade_author_gate_miss_detector.py",
    "post_cascade_author_gate_ui_audit.py",
    "post_cascade_author_gate_schema_audit.py",
    "post_cascade_ask_user_question_packet_audit.py",
    "post_cascade_author_gate_capture.py",
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


def _hooks_for_event(hooks_data: dict[str, Any], event: str) -> list[dict[str, Any]]:
    return hooks_data.get("hooks", {}).get(event, [])


def evaluate(hooks_data: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Evaluate all AG wiring invariants.
    Returns a list of violation dicts (empty = all pass).
    """
    violations: list[dict[str, Any]] = []

    post_cascade = _hooks_for_event(hooks_data, "post_cascade_response")
    pre_prompt = _hooks_for_event(hooks_data, "pre_user_prompt")

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
                f"pre_user_prompt does not contain {REQUIRED_PRE_PROMPT_HOOK}. "
                "AG audit hooks are wired but the pre-composition reminder is missing. "
                "Add pre_user_prompt_author_gate_reminder.py to pre_user_prompt with show_output=true."
            ),
        })
    elif not reminder_hook.get("show_output", False):
        violations.append({
            "invariant": "AG-WIRE-1",
            "severity": "ERROR",
            "message": (
                f"{REQUIRED_PRE_PROMPT_HOOK} is present in pre_user_prompt but "
                "show_output=false. Pipeline reminders will be invisible. "
                "Set show_output=true."
            ),
        })

    # AG-WIRE-2/3/4: required post_cascade audit hooks must be present and visible
    for req in REQUIRED_POST_CASCADE_HOOKS:
        script = req["script"]
        inv_id = req["id"]
        hook = post_by_name.get(script)
        if hook is None:
            violations.append({
                "invariant": inv_id,
                "severity": "ERROR",
                "message": (
                    f"post_cascade_response does not contain {script}. "
                    f"{req['description']}."
                ),
            })
        elif req["show_output"] and not hook.get("show_output", False):
            violations.append({
                "invariant": inv_id,
                "severity": "ERROR",
                "message": (
                    f"{script} is present in post_cascade_response but "
                    f"show_output=false — violations will be silently swallowed. "
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
