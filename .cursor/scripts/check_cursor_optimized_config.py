#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
EXPECTED_ALWAYS = {
    "000-agentic-core-operating-contract.mdc",
    "001-cursor-runtime-seam-execution.mdc",
    "002-pass-blocked-proof-contract.mdc",
}
REQUIRED_HOOK_EVENTS = {"beforeSubmitPrompt", "beforeShellExecution", "beforeMCPExecution", "beforeReadFile", "afterFileEdit", "stop"}


def rel(path: Path) -> str:
    return str(path.relative_to(PROJECT)).replace("\\", "/")


def parse_always(text: str) -> str | None:
    match = re.search(r"alwaysApply:\s*(true|false)", text)
    return match.group(1) if match else None


def main(strict: bool) -> int:
    failures = []
    warnings = []

    rules_dir = ROOT / "rules"
    always_true = set()
    for path in sorted(rules_dir.glob("*.mdc")):
        text = path.read_text(encoding="utf-8")
        value = parse_always(text)
        if value is None:
            failures.append({"type": "rule_missing_alwaysApply", "path": rel(path)})
        elif value == "true":
            always_true.add(path.name)
        if not text.startswith("---"):
            failures.append({"type": "rule_missing_frontmatter", "path": rel(path)})

    if always_true != EXPECTED_ALWAYS:
        failures.append({
            "type": "unexpected_always_on_rules",
            "expected": sorted(EXPECTED_ALWAYS),
            "actual": sorted(always_true),
        })

    plans_dir = ROOT / "plans"
    active_plan_files = [p for p in plans_dir.iterdir() if p.is_file()]
    allowed_active_plans = {"README.md", "CURSOR_RUNTIME_SEAM_TEMPLATE.md"}
    unexpected_active = sorted(p.name for p in active_plan_files if p.name not in allowed_active_plans)
    if unexpected_active:
        failures.append({
            "type": "active_plan_sprawl",
            "unexpected_active_plan_files": unexpected_active[:50],
            "count": len(unexpected_active),
        })

    historical_archive = ROOT / "plans" / "_archive" / "historical_plans_20260515_cursor_optimization"
    if not historical_archive.exists():
        failures.append({"type": "missing_historical_archive", "path": rel(historical_archive)})
    else:
        archived_count = len([p for p in historical_archive.rglob("*") if p.is_file()])
        if archived_count < 100:
            warnings.append({"type": "low_archived_plan_count", "count": archived_count})

    hooks_path = ROOT / "hooks.json"
    try:
        hooks = json.loads(hooks_path.read_text(encoding="utf-8"))
        events = set((hooks.get("hooks") or {}).keys())
        missing = sorted(REQUIRED_HOOK_EVENTS - events)
        if missing:
            failures.append({"type": "hook_event_mismatch", "missing": missing})
    except Exception as exc:
        failures.append({"type": "invalid_hooks_json", "error": str(exc)})

    # Hooks should not block legitimate Cursor config validation by treating .cursor or mcp.json alone as legacy.
    for hook_name in ("before_shell_execution.py", "before_submit_prompt.py", "before_mcp_execution.py"):
        path = ROOT / "hooks" / hook_name
        text = path.read_text(encoding="utf-8")
        suspicious = [token for token in ("'.cursor'", '".cursor"', "'mcp.json'", '"mcp.json"') if token in text]
        if suspicious:
            failures.append({"type": "overbroad_hook_token", "path": rel(path), "tokens": suspicious})

    for json_path in (ROOT / "mcp.json", ROOT / "hooks.json", ROOT / "migration_allowlist.json"):
        try:
            json.loads(json_path.read_text(encoding="utf-8"))
        except Exception as exc:
            failures.append({"type": "invalid_json", "path": rel(json_path), "error": str(exc)})

    result = {
        "status": "FAIL" if failures else "PASS",
        "failures": failures,
        "warnings": warnings,
        "always_on_rules": sorted(always_true),
        "active_plan_files": sorted(p.name for p in active_plan_files),
    }
    print(json.dumps(result, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    raise SystemExit(main(args.strict))
