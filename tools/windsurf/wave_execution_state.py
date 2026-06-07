"""
wave_execution_state.py — CLI to mark/unmark a multi-wave plan as in-progress.

Cursor Agent runs this at the start of Wave 1 and again after the final wave
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

Plan notion-plan-status-reconciliation-a3f2e1 (W1 extension): ``complete``
performs status reconciliation. When a plan completes its final wave but
has deferred scope items that are blocked (time-gated or volume-gated),
the CLI now auto-suggests flipping the Notion Status from "In Progress" to
"Waiting" and populates the "Waiting For" field with blocker descriptions.
This closes the status discipline gap identified in RCA of plan
notion-plan-identity-deferred-scope-a3b7e2.

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
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# Import the shared helpers without polluting sys.path globally.
_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO_ROOT / ".cursor" / "scripts" / "_legacy_windsurf"
sys.path.insert(0, str(_SCRIPTS))

import _wave_execution_state as wes  # noqa: E402
import _plan_registration as pr  # noqa: E402

# Deferred scope ledger path for status reconciliation
_DEFERRED_SCOPE_LEDGER = _REPO_ROOT / "artifacts" / "ledgers" / "deferred_scope_calibration.sqlite"

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
        "  with Slug, Status=Not Started (canonical), Exists On Disk=true, Plan File Path,\n"
        "  Summary, AI Summary (trailing space in property name).\n"
        "After posting, re-run this command. To force-refresh the local cache:\n"
        "  python ops_scripts/ci/check_plan_registration_freshness.py --refresh\n"
        "Bypass (rare): PLAN_REGISTRATION_BYPASS=1 (logged)\n"
        "See .cursor/rules/plan-registration-enforcement.md · constitutional §36.",
        file=sys.stderr,
    )
    return 2


def _read_deferred_scope_for_plan(plan_slug: str) -> list[dict[str, Any]]:
    """Query deferred scope ledger for items related to plan_slug.

    Returns list of dicts with keys: plan_slug, wave_id, phase_id,
    computed_p_band, factors_json, event_time_utc, status.
    Fail-open: returns empty list on any error.
    """
    if not _DEFERRED_SCOPE_LEDGER.exists():
        return []
    try:
        conn = sqlite3.connect(str(_DEFERRED_SCOPE_LEDGER), timeout=5)
        conn.row_factory = sqlite3.Row
        try:
            # Query predictions for this plan that haven't been bound to outcomes
            rows = conn.execute(
                """
                SELECT
                    prediction_json->>'plan_slug' as plan_slug,
                    prediction_json->>'wave_id' as wave_id,
                    prediction_json->>'phase_id' as phase_id,
                    prediction_json->>'computed_p_band' as computed_p_band,
                    prediction_json->>'factors' as factors_json,
                    event_time_utc,
                    status
                FROM events
                WHERE event_kind = 'deferred_scope_capture'
                  AND prediction_json->>'plan_slug' = ?
                  AND status = 'predicted'
                ORDER BY event_time_utc DESC
                """,
                (plan_slug,),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()
    except (sqlite3.Error, OSError):
        return []


def _is_gated_deferred_item(row: dict[str, Any]) -> tuple[bool, str | None]:
    """Analyze a deferred scope row to determine if it's gated.

    Returns (is_gated, gate_reason) where gate_reason is one of:
    - "time-gated: <description>"
    - "volume-gated: <description>"
    - None (if not gated)

    Gating detection:
    - time-gated: reason mentions "30-day", "30d", "data maturity", "time-gated"
    - volume-gated: reason mentions "volume", "threshold", "volume-gated"
    """
    factors_json = row.get("factors_json") or "{}"
    try:
        factors = json.loads(factors_json) if isinstance(factors_json, str) else factors_json
    except json.JSONDecodeError:
        factors = {}

    # Factors may contain explicit gating fields from v2 scorer
    if factors.get("time_gated"):
        return (True, f"time-gated: {factors.get('gate_description', 'pending time-based maturity')}")
    if factors.get("volume_gated"):
        return (True, f"volume-gated: {factors.get('gate_description', 'pending volume threshold')}")

    # Heuristic detection from phase_id or row context
    phase_id = (row.get("phase_id") or "").lower()
    if "time" in phase_id or "maturity" in phase_id or "30d" in phase_id:
        return (True, "time-gated: pending maturity criteria")
    if "volume" in phase_id or "threshold" in phase_id:
        return (True, "volume-gated: pending volume criteria")

    return (False, None)


def _analyze_deferred_scope_status(plan_slug: str) -> dict[str, Any]:
    """Analyze deferred scope for a plan and return status recommendation.

    Returns dict with keys:
    - has_deferred_items: bool
    - total_items: int
    - gated_items: int
    - ungated_items: int
    - all_gated: bool (True if has items and all are gated)
    - blocker_descriptions: list[str] (descriptions for gated items)
    - recommendation: "waiting" | "completed" | "in_progress"
    """
    items = _read_deferred_scope_for_plan(plan_slug)
    if not items:
        return {
            "has_deferred_items": False,
            "total_items": 0,
            "gated_items": 0,
            "ungated_items": 0,
            "all_gated": False,
            "blocker_descriptions": [],
            "recommendation": "completed",
        }

    gated_count = 0
    ungated_count = 0
    blockers: list[str] = []

    for item in items:
        is_gated, gate_reason = _is_gated_deferred_item(item)
        if is_gated:
            gated_count += 1
            if gate_reason:
                phase = item.get("phase_id", "unknown")
                blockers.append(f"{phase}: {gate_reason}")
        else:
            ungated_count += 1

    all_gated = gated_count > 0 and ungated_count == 0

    # Recommendation logic:
    # - If all remaining items are gated -> suggest Waiting
    # - If any ungated items exist -> keep In Progress (work remains)
    # - If no items at all -> Completed
    if all_gated:
        recommendation = "waiting"
    elif ungated_count > 0:
        recommendation = "in_progress"
    else:
        recommendation = "completed"

    return {
        "has_deferred_items": True,
        "total_items": len(items),
        "gated_items": gated_count,
        "ungated_items": ungated_count,
        "all_gated": all_gated,
        "blocker_descriptions": blockers,
        "recommendation": recommendation,
    }


def _notion_sync(plan: str, kind: str, wave: int | None = None, note: str | None = None) -> None:
    """Best-effort direct-HTTP Notion sync. Never raises; never blocks.

    Synthesizes a single ``WaveLifecycleMarker`` and runs it through
    ``wave_lifecycle_writer.apply_spec``. Failures are logged to
    ``artifacts/cursor/wave_lifecycle_notion.jsonl`` (by the writer) and
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


def _current_notion_status(plan: str) -> str | None:
    """Look up the current Notion Status for a plan slug. Fail-open (returns None)."""
    token = os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")
    if not token or os.environ.get("WAVE_LIFECYCLE_NOTION_BYPASS") == "1":
        return None
    sys.path.insert(0, str(_REPO_ROOT))
    try:
        from tools.notion import wave_lifecycle_writer as wlw  # noqa: WPS433
        page_id, props, _msg = wlw.find_plan_page(plan, token)
        if page_id:
            return wlw._extract_status(props)
    except (ImportError, OSError, ValueError):
        pass
    return None


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

    # Guard: do NOT flip a Completed plan back to In Progress.
    # This closes the race condition where a retrospective plan is created-and-
    # completed in the same turn and then `start` is inadvertently called.
    # Plan: notion-plan-status-hardening-e5f3a1 (W1.P1).
    current_status = _current_notion_status(plan)
    if current_status == "Completed":
        print(
            f"[wave-exec] NOTION_SYNC SKIPPED plan={plan} kind=wave_start "
            f"reason=status_already_completed (guard: notion-plan-status-hardening-e5f3a1)",
            file=sys.stderr,
        )
        return 0

    _notion_sync(plan, "wave_start", wave=1, note=note)
    return 0


def _notion_patch_status_and_waiting_for(
    plan_slug: str,
    new_status: str,
    waiting_for_text: str | None,
    token: str | None = None,
) -> dict[str, Any]:
    """Direct-HTTP PATCH to Notion Plans DB for status + Waiting For.

    Fail-open: returns {"ok": False, "error": ...} on any failure.
    Returns {"ok": True, "page_id": ...} on success.
    """
    result: dict[str, Any] = {"ok": False, "error": None, "page_id": None}
    if not token:
        result["error"] = "no token"
        return result

    # Import lazily to avoid startup deps
    sys.path.insert(0, str(_REPO_ROOT))
    try:
        from tools.notion._wave_lifecycle_helpers import (
            STATUS_WAITING,
            STATUS_COMPLETED,
            CANONICAL_STATUSES,
        )
        from tools.notion import wave_lifecycle_writer as wlw
    except ImportError as exc:
        result["error"] = f"import failed: {exc}"
        return result

    if new_status not in CANONICAL_STATUSES:
        result["error"] = f"non-canonical status: {new_status}"
        return result

    try:
        page_id, props, _ = wlw.find_plan_page(plan_slug, token)
        if not page_id:
            result["error"] = "plan page not found"
            return result

        # Build patch properties
        patch_props: dict[str, Any] = {
            "Status": {"select": {"name": new_status}},
        }
        if waiting_for_text:
            patch_props["Waiting For"] = {
                "rich_text": [{"text": {"content": waiting_for_text[:2000]}}]
            }

        ok, msg = wlw.apply_spec(
            wlw.NotionPatchSpec(
                slug=plan_slug,
                properties=patch_props,
                summary_append=None,
                reason=f"status_reconciliation:{new_status}",
            ),
            token=token,
        )
        result["ok"] = ok
        result["page_id"] = page_id if ok else None
        if not ok:
            result["error"] = msg
    except (OSError, ValueError) as exc:
        result["error"] = str(exc)

    return result


def _cmd_complete(plan: str, note: str | None = None) -> int:
    state = wes.is_active()
    if state is None:
        print(f"[wave-exec] COMPLETE plan={plan} (no active state to clear)")
    else:
        if state.get("plan") != plan:
            print(
                f"[wave-exec] WARNING: active plan is {state.get('plan')!r}, "
                f"requested complete={plan!r} — clearing anyway",
                file=sys.stderr,
            )
        removed = wes.clear()
        print(f"[wave-exec] COMPLETE plan={plan} removed={removed}")

    # Status reconciliation: analyze deferred scope and suggest Waiting if all gated
    deferred_analysis = _analyze_deferred_scope_status(plan)
    waiting_for_text: str | None = None

    if deferred_analysis["has_deferred_items"]:
        print(
            f"[wave-exec] DEFERRED_SCOPE plan={plan} "
            f"items={deferred_analysis['total_items']} "
            f"gated={deferred_analysis['gated_items']} "
            f"ungated={deferred_analysis['ungated_items']} "
            f"all_gated={deferred_analysis['all_gated']}",
            file=sys.stderr,
        )

        if deferred_analysis["all_gated"]:
            # Suggest Waiting status with blocker list
            blockers = deferred_analysis["blocker_descriptions"]
            waiting_for_text = "; ".join(blockers) if blockers else "Deferred items blocked on time/volume gates"
            print(
                f"[wave-exec] STATUS_RECOMMENDATION plan={plan} "
                f"recommendation=waiting reason=all_deferred_items_gated",
                file=sys.stderr,
            )

            # Attempt direct Notion PATCH for status flip
            token = os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")
            if token and os.environ.get("WAVE_LIFECYCLE_NOTION_BYPASS") != "1":
                patch_result = _notion_patch_status_and_waiting_for(
                    plan, "Waiting", waiting_for_text, token
                )
                if patch_result["ok"]:
                    print(
                        f"[wave-exec] STATUS_PATCHED plan={plan} "
                        f"status=Waiting page_id={patch_result['page_id']}",
                        file=sys.stderr,
                    )
                else:
                    print(
                        f"[wave-exec] STATUS_PATCH_FAILED plan={plan} "
                        f"error={patch_result.get('error')}",
                        file=sys.stderr,
                    )
            else:
                print(
                    f"[wave-exec] STATUS_PATCH_SKIPPED plan={plan} "
                    f"reason=no_token_or_bypass",
                    file=sys.stderr,
                )
        elif deferred_analysis["ungated_items"] > 0:
            print(
                f"[wave-exec] STATUS_RECOMMENDATION plan={plan} "
                f"recommendation=in_progress reason=ungated_items_remain",
                file=sys.stderr,
            )

    # Standard plan_complete marker (preserves original behavior)
    _notion_sync(plan, "plan_complete", note=note)
    return 0


def _prior_wave_completed(plan: str, current_wave: int) -> bool:
    """Check if prior wave (N-1) was marked complete for this plan.

    Scans the wave lifecycle log for a WAVE_COMPLETE entry.
    """
    if current_wave <= 1:
        return True  # Wave 1 has no prior

    log_path = _REPO_ROOT / "artifacts" / "windsurf" / "wave_lifecycle_capture.jsonl"
    if not log_path.exists():
        return False

    prior_wave = current_wave - 1
    try:
        with log_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    # Check for successful wave_complete events
                    if entry.get("event") == "capture_summary":
                        rows = entry.get("rows", [])
                        for row in rows:
                            if row.get("slug") == plan and row.get("ok"):
                                return True
                    # Also check direct wave_table_update events
                    if entry.get("event") == "wave_table_update":
                        if entry.get("slug") == plan and entry.get("kind") == "wave_complete":
                            return True
                except json.JSONDecodeError:
                    continue
    except OSError:
        pass
    return False


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

    # Phase 1.4: warn if prior wave not marked complete
    if not _prior_wave_completed(plan, wave):
        print(
            f"[wave-exec] WARNING: W{wave} progress recorded but W{wave-1} "
            f"has no WAVE_COMPLETE marker — plan .md and Notion may be stale",
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
