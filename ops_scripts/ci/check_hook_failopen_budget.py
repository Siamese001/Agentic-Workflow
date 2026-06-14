#!/usr/bin/env python3
"""Hook fail-open budget gate (W2 claude-enforcement-runtime-truth-hardening).

Governance hooks fail OPEN — they allow when their delegated backend is missing / times out /
errors, so a broken gate never wedges a turn. That safety property is correct, but a *silent*
fail-open means enforcement can be dead while looking alive. W2 added a dedicated fail-open
ledger (``artifacts/governance/hook_failopen_receipts.jsonl``, written by
``lib.claude_hook_common.write_failopen_receipt``); this gate makes that ledger countable and,
under strict mode, blockable.

Checks
------
A. critical_target_missing — every CRITICAL registered hook (UserPromptSubmit = pre-turn,
   PreToolUse = pre-tool) MUST have its command target file on disk. A missing critical hook
   target means that enforcement is wired in settings but cannot run at all → ERROR.
B. critical_failopen_regression — count CRITICAL_PRETURN/CRITICAL_PRETOOL ledger rows per hook;
   anything above the acknowledged ratchet baseline (default 0) is a regression → ERROR. To
   acknowledge a known/intended critical fail-open, re-baseline with ``--init``.
C. advisory_capture — ADVISORY_CAPTURE / POSTTURN_AUDIT rows are reported as WARN only.

Modes
-----
* Advisory (default): always exit 0; print the table + any ERROR/WARN lines. CI gets visibility.
* Fail-closed (``HOOK_FAILOPEN_BUDGET_FAIL_CLOSED=1``): exit 1 if any ERROR.
* Bypass (``HOOK_FAILOPEN_BUDGET_BYPASS=1``): exit 0 immediately (scripted/batch runs).

Usage
-----
  python ops_scripts/ci/check_hook_failopen_budget.py            # advisory report
  python ops_scripts/ci/check_hook_failopen_budget.py --json     # machine-readable
  python ops_scripts/ci/check_hook_failopen_budget.py --init     # write/refresh the ratchet baseline
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

# ops_scripts/ci/<this> -> repo root
REPO_ROOT = Path(__file__).resolve().parents[2]
SETTINGS = REPO_ROOT / ".claude" / "settings.json"
LEDGER = REPO_ROOT / "artifacts" / "governance" / "hook_failopen_receipts.jsonl"
BASELINE = REPO_ROOT / "ops_scripts" / "ci" / "baselines" / "hook_failopen_budget.json"

CRITICAL = {"CRITICAL_PRETURN", "CRITICAL_PRETOOL"}
# settings.json event -> whether a registered hook under it is a critical enforcement surface
_CRITICAL_EVENTS = {"UserPromptSubmit", "PreToolUse"}

_PATH_RE = re.compile(r'([^\s"\']*\.(?:py|sh))')


def _bypass() -> bool:
    return os.environ.get("HOOK_FAILOPEN_BUDGET_BYPASS", "").strip().lower() in ("1", "true", "yes")


def _fail_closed() -> bool:
    return os.environ.get("HOOK_FAILOPEN_BUDGET_FAIL_CLOSED", "").strip().lower() in ("1", "true", "yes")


def _resolve_target(command: str) -> Path | None:
    """Extract the hook's script path from a settings.json command string and resolve it."""
    match = _PATH_RE.search(command or "")
    if not match:
        return None
    raw = match.group(1).strip().strip('"').strip("'")
    raw = raw.replace("$CLAUDE_PROJECT_DIR", "").replace("${CLAUDE_PROJECT_DIR}", "")
    raw = raw.lstrip("/\\").replace("\\", "/")
    return (REPO_ROOT / raw).resolve()


def load_registered_hooks() -> list[dict[str, Any]]:
    """Return [{event, command, target, target_exists, critical}] for every registered hook."""
    try:
        settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    out: list[dict[str, Any]] = []
    for event, groups in (settings.get("hooks") or {}).items():
        for group in groups or []:
            for hook in group.get("hooks") or []:
                command = str(hook.get("command") or "")
                target = _resolve_target(command)
                out.append(
                    {
                        "event": event,
                        "command": command,
                        "target": str(target) if target else "",
                        "target_exists": bool(target and target.is_file()),
                        "critical": event in _CRITICAL_EVENTS,
                    }
                )
    return out


def load_ledger_counts() -> dict[str, dict[str, int]]:
    """Return {hook_name: {criticality: count}} from the fail-open ledger."""
    counts: dict[str, dict[str, int]] = {}
    if not LEDGER.is_file():
        return counts
    try:
        lines = LEDGER.read_text(encoding="utf-8").splitlines()
    except OSError:
        return counts
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(row, dict):
            continue
        hook = str(row.get("hook") or "?")
        crit = str(row.get("criticality") or "?")
        counts.setdefault(hook, {}).setdefault(crit, 0)
        counts[hook][crit] += 1
    return counts


def load_baseline() -> dict[str, int]:
    try:
        data = json.loads(BASELINE.read_text(encoding="utf-8"))
        return {str(k): int(v) for k, v in data.get("critical_per_hook", {}).items()}
    except (OSError, json.JSONDecodeError, ValueError, AttributeError):
        return {}


def evaluate() -> dict[str, Any]:
    hooks = load_registered_hooks()
    counts = load_ledger_counts()
    baseline = load_baseline()

    errors: list[str] = []
    warns: list[str] = []

    # Check A — critical registered hook targets must exist.
    for h in hooks:
        if h["critical"] and not h["target_exists"]:
            errors.append(
                f"critical_target_missing: {h['event']} hook target absent -> {h['command']}"
            )

    # Check B / C — ledger counts vs baseline.
    per_hook_critical: dict[str, int] = {}
    for hook, by_crit in counts.items():
        crit_total = sum(n for c, n in by_crit.items() if c in CRITICAL)
        per_hook_critical[hook] = crit_total
        allowed = baseline.get(hook, 0)
        if crit_total > allowed:
            errors.append(
                f"critical_failopen_regression: {hook} has {crit_total} critical fail-open(s) "
                f"(baseline {allowed}) — investigate the degraded backend or re-baseline with --init"
            )
        advisory_total = sum(n for c, n in by_crit.items() if c not in CRITICAL)
        if advisory_total:
            warns.append(f"advisory_failopen: {hook} has {advisory_total} non-critical fail-open(s)")

    return {
        "hooks": hooks,
        "counts": counts,
        "per_hook_critical": per_hook_critical,
        "baseline": baseline,
        "errors": errors,
        "warns": warns,
    }


def _write_baseline(result: dict[str, Any]) -> None:
    BASELINE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "_doc": "Acknowledged critical fail-open counts per hook. Raise only via deliberate --init.",
        "critical_per_hook": result["per_hook_critical"],
    }
    BASELINE.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Hook fail-open budget gate")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--init", action="store_true", help="write/refresh the ratchet baseline from current counts")
    args = parser.parse_args(argv)

    if _bypass():
        if not args.json:
            print("HOOK_FAILOPEN_BUDGET: bypass (HOOK_FAILOPEN_BUDGET_BYPASS=1)")
        return 0

    result = evaluate()

    if args.init:
        _write_baseline(result)
        if not args.json:
            print(f"HOOK_FAILOPEN_BUDGET: baseline written -> {BASELINE}")
        return 0

    fail_closed = _fail_closed()
    verdict = "FAIL" if (result["errors"] and fail_closed) else ("ERROR_ADVISORY" if result["errors"] else "OK")

    if args.json:
        print(json.dumps({**{k: result[k] for k in ("per_hook_critical", "errors", "warns", "baseline")}, "verdict": verdict, "fail_closed": fail_closed}, indent=2))
    else:
        print("=== Hook fail-open budget ===")
        crit_hooks = [h for h in result["hooks"] if h["critical"]]
        print(f"Registered critical hooks: {len(crit_hooks)}  (missing target: {sum(1 for h in crit_hooks if not h['target_exists'])})")
        if result["per_hook_critical"]:
            print("Critical fail-opens by hook (count | baseline):")
            for hook in sorted(result["per_hook_critical"]):
                print(f"  {hook}: {result['per_hook_critical'][hook]} | {result['baseline'].get(hook, 0)}")
        else:
            print("Critical fail-opens by hook: none recorded")
        for w in result["warns"]:
            print(f"WARN  {w}")
        for e in result["errors"]:
            print(f"ERROR {e}")
        print(f"VERDICT: {verdict}  (fail_closed={fail_closed}; flip with HOOK_FAILOPEN_BUDGET_FAIL_CLOSED=1)")

    return 1 if verdict == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
