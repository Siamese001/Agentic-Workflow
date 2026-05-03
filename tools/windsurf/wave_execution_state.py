"""
wave_execution_state.py — CLI to mark/unmark a multi-wave plan as in-progress.

Cascade runs this at the start of Wave 1 and again after the final wave
completes. While active, pre_mcp_gate.py blocks Notion MCP calls so all
Notion writes are deferred to the end of the plan (avoids mid-wave stalls
from the §25 remote-MCP serialization rule).

Constitutional §36 extension (2026-05-03): ``start`` refuses to mark a plan
as in-progress when the plan is not registered in the Notion Plans DB.
Chokepoint rationale: this CLI is the single canonical entry for wave
execution, so one gate covers all wave work. Bypass: PLAN_REGISTRATION_BYPASS=1.

Usage:
    python tools/windsurf/wave_execution_state.py start --plan <slug-6hex>
    python tools/windsurf/wave_execution_state.py complete --plan <slug-6hex>
    python tools/windsurf/wave_execution_state.py status
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Import the shared helpers without polluting sys.path globally.
_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO_ROOT / ".windsurf" / "scripts"
sys.path.insert(0, str(_SCRIPTS))

import _wave_execution_state as wes  # noqa: E402
import _plan_registration as pr  # noqa: E402

_BYPASS_LOG = _REPO_ROOT / "artifacts" / "windsurf" / "plan_registration_bypasses.jsonl"


def _log_bypass(plan: str, source: str, reason: str | None) -> None:
    """Append a bypass row for audit. Best-effort; never raises."""
    try:
        _BYPASS_LOG.parent.mkdir(parents=True, exist_ok=True)
        row = {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "plan": plan,
            "source": source,
            "reason": reason,
            "env": "PLAN_REGISTRATION_BYPASS=1",
        }
        with _BYPASS_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    except OSError:
        pass


def _check_plan_registration(plan: str) -> int:
    """Return 0 (allow) or 2 (block) for a wave-start against ``plan``.

    Block message is printed to stderr. Fails OPEN when cache is missing
    AND no Notion token is available — otherwise CI runs / local dev
    without network would be permanently blocked.
    """
    if os.environ.get("PLAN_REGISTRATION_BYPASS") == "1":
        res = pr.check_registration(plan)
        _log_bypass(plan, res.source, res.reason)
        print(
            f"[wave-exec] PLAN_REGISTRATION_BYPASS=1 — allowing wave start "
            f"for unverified plan {plan!r} (source={res.source}, reason={res.reason})",
            file=sys.stderr,
        )
        return 0

    cache = pr.read_cache()
    res = pr.check_registration(plan, cache=cache)
    if res.registered:
        return 0

    has_token = bool(os.environ.get("NOTION_API_KEY") or os.environ.get("NOTION_TOKEN"))
    if res.source in ("cache_missing", "cache_stale") and not has_token:
        print(
            f"[wave-exec] WARNING: plan {plan!r} registration status unknown "
            f"(source={res.source}, NOTION_API_KEY unset) — allowing wave start. "
            f"Refresh the cache with "
            f"`python ops_scripts/ci/check_plan_registration_freshness.py` "
            f"when a token is available.",
            file=sys.stderr,
        )
        return 0

    print(
        f"[wave-exec] BLOCKED: plan {plan!r} not registered in Notion Plans DB.\n"
        f"  Cache source: {res.source}\n"
        f"  Reason:       {res.reason}\n"
        f"  Status:       {res.status}\n"
        "Required: API-post-page into Plans DB (data source "
        "ac53d31b-3068-4039-9ebe-856c12caab32)\n"
        "  with Slug, Status (Live|Draft), Exists On Disk=true, Plan File Path,\n"
        "  Summary, AI Summary (trailing space in property name).\n"
        "After posting, re-run this command. To force-refresh the local cache:\n"
        "  python ops_scripts/ci/check_plan_registration_freshness.py --refresh\n"
        "Bypass (rare): PLAN_REGISTRATION_BYPASS=1 (logged)\n"
        "See .windsurf/rules/plan-registration-enforcement.md · constitutional §36.",
        file=sys.stderr,
    )
    return 2


def _cmd_start(plan: str) -> int:
    rc = _check_plan_registration(plan)
    if rc != 0:
        return rc

    prior = wes.is_active()
    path = wes.set_active(plan)
    if prior and prior.get("plan") != plan:
        print(
            f"[wave-exec] WARNING: overwriting prior active plan "
            f"{prior.get('plan')!r} with {plan!r}",
            file=sys.stderr,
        )
    # Mark queue row as registered (best-effort; no-op if slug not queued).
    try:
        pr.mark_registered(plan)
    except (OSError, ValueError):
        pass
    print(f"[wave-exec] START plan={plan} state={path}")
    return 0


def _cmd_complete(plan: str) -> int:
    state = wes.is_active()
    if state is None:
        print(f"[wave-exec] COMPLETE plan={plan} (no active state to clear)")
        return 0
    if state.get("plan") != plan:
        print(
            f"[wave-exec] WARNING: active plan is {state.get('plan')!r}, "
            f"requested complete={plan!r} — clearing anyway",
            file=sys.stderr,
        )
    removed = wes.clear()
    print(f"[wave-exec] COMPLETE plan={plan} removed={removed}")
    return 0


def _cmd_status() -> int:
    state = wes.is_active()
    if state is None:
        print(json.dumps({"active": False}))
        return 0
    print(json.dumps({"active": True, **state}, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_start = sub.add_parser("start", help="Mark a multi-wave plan as in-progress")
    p_start.add_argument("--plan", required=True, help="Plan slug (e.g., 'my-plan-abc123')")

    p_complete = sub.add_parser("complete", help="Clear the active multi-wave plan")
    p_complete.add_argument("--plan", required=True, help="Plan slug being completed")

    sub.add_parser("status", help="Show active plan state (JSON)")

    args = parser.parse_args(argv)

    if args.command == "start":
        return _cmd_start(args.plan)
    if args.command == "complete":
        return _cmd_complete(args.plan)
    if args.command == "status":
        return _cmd_status()
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
