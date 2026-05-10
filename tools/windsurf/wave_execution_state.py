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

Plan notion-wave-lifecycle-autosync-f4a2b8 (W2 extension): ``start`` /
``complete`` / ``wave-progress`` now emit best-effort direct-HTTP Notion
writes via ``tools.notion.wave_lifecycle_writer``. The writer bypasses the
MCP layer entirely (no ``<invoke name="mcp*_API-*">`` tags emitted), so the
plan-wave-deferral rule and §25 serialization rule do NOT block these
writes. Failure mode is fail-soft — wave state is the source of truth;
Notion sync is best-effort. Bypass: WAVE_LIFECYCLE_NOTION_BYPASS=1.

Usage:
    python tools/windsurf/wave_execution_state.py start --plan <slug-6hex>
    python tools/windsurf/wave_execution_state.py complete --plan <slug-6hex>
    python tools/windsurf/wave_execution_state.py wave-progress --plan <slug-6hex> --wave N
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


def _notion_sync(plan: str, kind: str, wave: int | None = None, note: str | None = None) -> None:
    """Best-effort direct-HTTP Notion sync. Never raises; never blocks.

    Synthesizes a single ``WaveLifecycleMarker`` and runs it through
    ``wave_lifecycle_writer.apply_spec``. Failures are logged to
    ``artifacts/windsurf/wave_lifecycle_notion.jsonl`` (by the writer) and
    swallowed here so wave state remains the source of truth.

    Skipped when ``WAVE_LIFECYCLE_NOTION_BYPASS=1`` is set or when no
    ``NOTION_TOKEN`` / ``NOTION_API_KEY`` is available.
    """
    if os.environ.get("WAVE_LIFECYCLE_NOTION_BYPASS") == "1":
        print(
            f"[wave-exec] WAVE_LIFECYCLE_NOTION_BYPASS=1 — skipping Notion sync "
            f"({kind} plan={plan} wave={wave})",
            file=sys.stderr,
        )
        return
    if not (os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")):
        print(
            f"[wave-exec] NOTION_TOKEN unset — skipping Notion sync "
            f"({kind} plan={plan} wave={wave})",
            file=sys.stderr,
        )
        return
    # Defer the import so a missing tools/notion package never breaks wave-state.
    sys.path.insert(0, str(_REPO_ROOT))
    try:
        from tools.notion._wave_lifecycle_helpers import (  # noqa: WPS433
            WaveLifecycleMarker,
            patch_for_marker,
        )
        from tools.notion import wave_lifecycle_writer as wlw  # noqa: WPS433
    except ImportError as exc:
        print(f"[wave-exec] Notion sync import failed: {exc!r}", file=sys.stderr)
        return

    marker = WaveLifecycleMarker(kind=kind, slug=plan, wave=wave, note=note)
    token = os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")
    current_status: str | None = None
    try:
        page_id, props, _msg = wlw.find_plan_page(plan, token)
        if page_id:
            current_status = wlw._extract_status(props)
    except (OSError, ValueError) as exc:
        print(f"[wave-exec] Notion lookup failed: {exc!r}", file=sys.stderr)
        return

    spec = patch_for_marker(marker, current_status)
    try:
        ok, msg = wlw.apply_spec(spec, token=token)
    except (OSError, ValueError) as exc:
        print(f"[wave-exec] Notion apply failed: {exc!r}", file=sys.stderr)
        return
    tag = "OK" if ok else "WARN"
    print(
        f"[wave-exec] NOTION_SYNC {tag} plan={plan} kind={kind} "
        f"wave={wave} msg={msg} reason={spec.reason}",
        file=sys.stderr,
    )


def _cmd_start(plan: str, note: str | None = None) -> int:
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
    _notion_sync(plan, "wave_start", wave=1, note=note)
    return 0


def _cmd_complete(plan: str, note: str | None = None) -> int:
    state = wes.is_active()
    if state is None:
        print(f"[wave-exec] COMPLETE plan={plan} (no active state to clear)")
        _notion_sync(plan, "plan_complete", note=note)
        return 0
    if state.get("plan") != plan:
        print(
            f"[wave-exec] WARNING: active plan is {state.get('plan')!r}, "
            f"requested complete={plan!r} — clearing anyway",
            file=sys.stderr,
        )
    removed = wes.clear()
    print(f"[wave-exec] COMPLETE plan={plan} removed={removed}")
    _notion_sync(plan, "plan_complete", note=note)
    return 0


def _cmd_wave_progress(plan: str, wave: int, note: str | None = None) -> int:
    """Log wave completion progress without changing wave-state.

    Used between waves to surface progress in Notion. Does NOT clear active
    state (use ``complete`` for that). Writes a ``[Wave-Log <ts>] W{N} DONE``
    line to the plan's Summary property. When ``--note`` is supplied the
    line is suffixed with ``— {note}`` (capped at ~240 chars) so the Notion
    Summary column carries scope info per wave instead of bare timestamps.
    """
    state = wes.is_active()
    if state is None:
        print(
            f"[wave-exec] WARNING: wave-progress called for {plan!r} but no plan is active",
            file=sys.stderr,
        )
    elif state.get("plan") != plan:
        print(
            f"[wave-exec] WARNING: active plan is {state.get('plan')!r}, "
            f"requested wave-progress={plan!r}",
            file=sys.stderr,
        )
    print(f"[wave-exec] WAVE_PROGRESS plan={plan} wave={wave}")
    _notion_sync(plan, "wave_complete", wave=wave, note=note)
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

    _NOTE_HELP = (
        "Optional high-signal one-liner appended to the Notion Summary log line "
        "(e.g. '4 files, +12 tests, scope=summary-signal'). Capped at ~240 chars; "
        "whitespace collapsed."
    )

    p_start = sub.add_parser("start", help="Mark a multi-wave plan as in-progress")
    p_start.add_argument("--plan", required=True, help="Plan slug (e.g., 'my-plan-abc123')")
    p_start.add_argument("--note", help=_NOTE_HELP)

    p_complete = sub.add_parser("complete", help="Clear the active multi-wave plan")
    p_complete.add_argument("--plan", required=True, help="Plan slug being completed")
    p_complete.add_argument("--note", help=_NOTE_HELP)

    p_progress = sub.add_parser(
        "wave-progress",
        help="Log wave completion to Notion without clearing wave-state",
    )
    p_progress.add_argument("--plan", required=True, help="Plan slug")
    p_progress.add_argument("--wave", type=int, required=True, help="Wave number just completed")
    p_progress.add_argument("--note", help=_NOTE_HELP)

    sub.add_parser("status", help="Show active plan state (JSON)")

    args = parser.parse_args(argv)

    if args.command == "start":
        return _cmd_start(args.plan, note=getattr(args, "note", None))
    if args.command == "complete":
        return _cmd_complete(args.plan, note=getattr(args, "note", None))
    if args.command == "wave-progress":
        return _cmd_wave_progress(args.plan, args.wave, note=getattr(args, "note", None))
    if args.command == "status":
        return _cmd_status()
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
