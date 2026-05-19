#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent

# Import shared measurement (repo root on path for ops_scripts.ci package).
_REPO_ROOT = PROJECT
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
from ops_scripts.ci.governance_tier_measurement import (  # noqa: E402
    OPTION_A_ALWAYS_APPLY,
    OPTION_A_TRANSITIONAL_EXTRAS,
)

REQUIRED_HOOK_EVENTS = {
    "beforeSubmitPrompt",
    "beforeShellExecution",
    "beforeMCPExecution",
    "beforeReadFile",
    "afterFileEdit",
    "stop",
}
# Same deny surface as ``.cursor/hooks/lib/cursor_hook_common.py`` (hook runtime).
LEGACY_HOOK_DENY_TOKENS = (
    ".windsurf",
    "mcp_config.json",
    "post_cursor_agent",
    "pre_cursor_agent",
    "Cursor Agent",
    "Windsurf",
)


def rel(path: Path) -> str:
    return str(path.relative_to(PROJECT)).replace("\\", "/")


def parse_always(text: str) -> str | None:
    import re

    match = re.search(r"alwaysApply:\s*(true|false)", text)
    return match.group(1) if match else None


def main(strict: bool) -> int:
    failures = []
    warnings = []

    rules_dir = ROOT / "rules"
    always_true: set[str] = set()
    for path in sorted(rules_dir.glob("*.mdc")):
        text = path.read_text(encoding="utf-8")
        value = parse_always(text)
        if value is None:
            failures.append({"type": "rule_missing_alwaysApply", "path": rel(path)})
        elif value == "true":
            always_true.add(path.name)
        if not text.startswith("---"):
            failures.append({"type": "rule_missing_frontmatter", "path": rel(path)})

    missing_option_a = sorted(OPTION_A_ALWAYS_APPLY - always_true)
    if missing_option_a:
        failures.append(
            {
                "type": "option_a_missing_always_apply",
                "expected": sorted(OPTION_A_ALWAYS_APPLY),
                "missing": missing_option_a,
                "actual": sorted(always_true),
            }
        )

    unexpected_extras = sorted(
        always_true - OPTION_A_ALWAYS_APPLY - OPTION_A_TRANSITIONAL_EXTRAS
    )
    if unexpected_extras:
        failures.append(
            {
                "type": "unexpected_always_apply_rules",
                "policy_option": "A",
                "unexpected": unexpected_extras,
                "actual": sorted(always_true),
            }
        )

    transitional = sorted(always_true & OPTION_A_TRANSITIONAL_EXTRAS)
    if transitional:
        warnings.append(
            {
                "type": "option_a_transitional_drift",
                "policy_option": "A",
                "pending_w1_demotion": transitional,
                "message": "W1 will demote these to alwaysApply:false per Option A",
            }
        )

    plans_dir = ROOT / "plans"
    active_plan_files = [p for p in plans_dir.iterdir() if p.is_file()] if plans_dir.is_dir() else []
    allowed_active_plans = {"README.md", "CURSOR_RUNTIME_SEAM_TEMPLATE.md"}
    unexpected_active = sorted(
        p.name for p in active_plan_files if p.name not in allowed_active_plans
    )
    if unexpected_active:
        warnings.append(
            {
                "type": "active_plan_sprawl_measurement",
                "count": len(unexpected_active),
                "sample": unexpected_active[:20],
                "message": "Counted for W0 inventory; archive is W3 scope (not a config FAIL)",
            }
        )

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

    for hook_name in ("before_shell_execution.py", "before_submit_prompt.py", "before_mcp_execution.py"):
        path = ROOT / "hooks" / hook_name
        text = path.read_text(encoding="utf-8")
        hits = [token for token in LEGACY_HOOK_DENY_TOKENS if token in text]
        if hits:
            failures.append(
                {
                    "type": "legacy_execution_token_in_hook",
                    "path": rel(path),
                    "tokens": hits,
                }
            )

    for json_path in (ROOT / "mcp.json", ROOT / "hooks.json", ROOT / "migration_allowlist.json"):
        try:
            json.loads(json_path.read_text(encoding="utf-8"))
        except Exception as exc:
            failures.append({"type": "invalid_json", "path": rel(json_path), "error": str(exc)})

    result = {
        "status": "FAIL" if failures else "PASS",
        "policy_option": "A",
        "failures": failures,
        "warnings": warnings,
        "always_apply_rules": sorted(always_true),
        "option_a_target_always_apply": sorted(OPTION_A_ALWAYS_APPLY),
        "active_plan_files_count": len(active_plan_files),
    }
    print(json.dumps(result, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    raise SystemExit(main(args.strict))
