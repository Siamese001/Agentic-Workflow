#!/usr/bin/env python3
"""
recover_deferred_scope_pendings.py — retry unresolved DEFERRED_SCOPE auto-posts.

Scans `artifacts/windsurf/deferred_scope_capture.jsonl` for entries with
`kind` in `pending_no_token`, `post_http_error`, `post_transport_error`,
`post_decode_error` that have NOT been superseded by a later `auto_posted`
or `confirmed_by_receipt` for the same (plan, wave, phase) key. Attempts
a fresh POST to Notion Wave/Phase Convergence DB for each.

Recovery logic is idempotent — re-running this script is safe. Successful
posts append `kind=auto_posted` records (with `recovered_from=<ts>` marker)
so subsequent runs treat them as resolved.

Usage:
    python tools/reports/recover_deferred_scope_pendings.py           # dry-run report
    python tools/reports/recover_deferred_scope_pendings.py --apply   # retry POSTs
    python tools/reports/recover_deferred_scope_pendings.py --json    # machine output

Env:
    NOTION_TOKEN or NOTION_API_KEY (required for --apply)

Fail policy: OPEN at process level (exits 0 unless --apply + hard failure).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
CAPTURE_LOG = REPO_ROOT / "artifacts" / "windsurf" / "deferred_scope_capture.jsonl"

import sys as _sys

_sys.path.insert(0, str(Path(REPO_ROOT) / ".windsurf" / "scripts"))
from _notion_constants import (  # noqa: E402
    NOTION_API_VERSION,
    NOTION_HTTP_TIMEOUT_S,
    NOTION_POST_URL,
    WAVE_PHASE_DB_ID,
)


PENDING_KINDS = {
    "pending_no_token",
    "post_http_error",
    "post_transport_error",
    "post_decode_error",
}
RESOLVED_KINDS = {"auto_posted", "confirmed_by_receipt", "skipped_recent_duplicate"}

# Reuse scorer for recomputing band on retry
sys.path.insert(0, str(REPO_ROOT))
try:
    from tools.priority.deferred_scope_scorer import score_deferred_scope  # type: ignore
except ImportError:
    score_deferred_scope = None  # type: ignore[assignment]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _utc_today_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _load_jsonl() -> list[dict[str, Any]]:
    if not CAPTURE_LOG.exists():
        return []
    records: list[dict[str, Any]] = []
    try:
        with CAPTURE_LOG.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except (json.JSONDecodeError, ValueError):
                    continue
    except OSError:
        return []
    return records


def _marker_key(marker: dict[str, str]) -> str:
    return f"{marker.get('plan', '')}|{marker.get('wave', '')}|{marker.get('phase', '')}"


def _find_unresolved_pendings(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """For each (plan, wave, phase), find the latest pending not followed by a resolution."""
    # Group by key; keep last record of each kind-class
    last_pending: dict[str, dict[str, Any]] = {}
    last_resolved_ts: dict[str, str] = {}

    for rec in records:
        marker = rec.get("marker") or {}
        if not marker:
            continue
        key = _marker_key(marker)
        ts = rec.get("timestamp", "")
        kind = rec.get("kind", "")
        if kind in PENDING_KINDS:
            # Keep most recent pending per key
            existing = last_pending.get(key)
            if not existing or existing.get("timestamp", "") < ts:
                last_pending[key] = rec
        elif kind in RESOLVED_KINDS:
            if last_resolved_ts.get(key, "") < ts:
                last_resolved_ts[key] = ts

    # Pending is unresolved if no resolution newer than it
    unresolved: list[dict[str, Any]] = []
    for key, rec in last_pending.items():
        pending_ts = rec.get("timestamp", "")
        resolved_ts = last_resolved_ts.get(key, "")
        if resolved_ts >= pending_ts:
            continue
        unresolved.append(rec)
    return unresolved


def _notion_token() -> str | None:
    return os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")


def _build_notion_payload(marker: dict[str, str], band: str, impact: float) -> dict[str, Any]:
    plan = marker["plan"]
    if plan.startswith("NEW:"):
        plan_file = f"{plan[4:]}.md"
    else:
        plan_file = plan if plan.endswith(".md") else f"{plan}.md"

    wave = marker["wave"]
    phase = marker["phase"]
    reason = marker.get("reason", "(no reason)")
    layer = marker.get("layer", "")
    fan_in = marker.get("fan_in", "0")
    surface = marker.get("surface", "None")
    gap = marker.get("coverage_gap_pct", "0")
    try:
        est_tokens = int(marker.get("est_tokens", "0"))
    except ValueError:
        est_tokens = 0

    phase_title = f"[{band}] {wave} {phase} — {reason}"
    sub_wave = f"{wave}-{band}-AUTO-RECOVERED"
    blocking = (
        f"{reason}. Layer={layer}, fan_in={fan_in}, surface={surface}, "
        f"coverage_gap_pct={gap}. Priority impact: {impact}. "
        f"RECOVERED from pending entry on {_utc_today_iso()}."
    )
    parent = (
        f"{plan_file}: deferred scope recovered {_utc_today_iso()} via recover_deferred_scope_pendings.py."
    )

    return {
        "parent": {"database_id": WAVE_PHASE_DB_ID},
        "properties": {
            "Phase Title": {"title": [{"text": {"content": phase_title}}]},
            "Phase ID": {"rich_text": [{"text": {"content": phase}}]},
            "Wave ID": {"rich_text": [{"text": {"content": wave}}]},
            "Sub-Wave": {"rich_text": [{"text": {"content": sub_wave}}]},
            "Dependencies": {
                "rich_text": [
                    {
                        "text": {
                            "content": "Recovered from prior session pending state. Review before execution."
                        }
                    }
                ]
            },
            "Success Criteria": {
                "rich_text": [{"text": {"content": "See Blocking Items for scope; fill on execution start."}}]
            },
            "Files In Scope": {"rich_text": [{"text": {"content": "TBD — fill on execution start."}}]},
            "Parent Plan Summary": {"rich_text": [{"text": {"content": parent}}]},
            "Plan File": {"rich_text": [{"text": {"content": plan_file}}]},
            "Status": {"select": {"name": "Todo"}},
            "Est Tokens": {"number": est_tokens},
            "Blocking Items": {"rich_text": [{"text": {"content": blocking}}]},
        },
    }


def _notion_post(payload: dict[str, Any], token: str) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        NOTION_POST_URL,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_API_VERSION,
        },
    )
    with urllib.request.urlopen(req, timeout=NOTION_HTTP_TIMEOUT_S) as resp:
        data = resp.read().decode("utf-8")
    return json.loads(data) if data else {}


def _append_recovery_record(record: dict[str, Any]) -> None:
    CAPTURE_LOG.parent.mkdir(parents=True, exist_ok=True)
    try:
        with CAPTURE_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as exc:
        print(f"[recover] log write failed: {exc}", file=sys.stderr)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="recover_deferred_scope_pendings",
        description="Retry unresolved DEFERRED_SCOPE auto-posts.",
    )
    p.add_argument(
        "--apply",
        action="store_true",
        help="Actually retry POSTs. Default is dry-run report.",
    )
    p.add_argument("--json", action="store_true", help="Emit JSON output")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    records = _load_jsonl()
    unresolved = _find_unresolved_pendings(records)

    if not unresolved:
        msg = {"unresolved_count": 0, "message": "no unresolved pendings"}
        print(json.dumps(msg, indent=2) if args.json else msg["message"])
        return 0

    if not args.apply:
        if args.json:
            print(
                json.dumps(
                    {
                        "unresolved_count": len(unresolved),
                        "pendings": [
                            {
                                "timestamp": r.get("timestamp"),
                                "kind": r.get("kind"),
                                "key": _marker_key(r.get("marker", {})),
                                "marker": r.get("marker", {}),
                            }
                            for r in unresolved
                        ],
                    },
                    indent=2,
                )
            )
        else:
            print(f"Unresolved pendings: {len(unresolved)}")
            for r in unresolved:
                print(f"  - {r.get('timestamp')} [{r.get('kind')}] {_marker_key(r.get('marker', {}))}")
            print("\nRe-run with --apply to retry POSTs.")
        return 0

    # --apply path
    token = _notion_token()
    if not token:
        print("[recover] NOTION_TOKEN not set; cannot retry", file=sys.stderr)
        return 2
    if score_deferred_scope is None:
        print("[recover] scorer unavailable; cannot retry", file=sys.stderr)
        return 2

    succeeded = 0
    failed = 0
    results: list[dict[str, Any]] = []

    for pending in unresolved:
        marker = pending.get("marker", {})
        try:
            result = score_deferred_scope(
                layer=marker.get("layer", "L1"),
                fan_in=int(marker.get("fan_in", 0)),
                surface=marker.get("surface", "None"),
                coverage_gap_pct=float(marker.get("coverage_gap_pct", 0.0)),
            )
        except (ValueError, TypeError) as exc:
            failed += 1
            record = {
                "timestamp": _utc_now_iso(),
                "kind": "recovery_scoring_error",
                "error": str(exc),
                "marker": marker,
                "recovered_from": pending.get("timestamp"),
            }
            _append_recovery_record(record)
            results.append(record)
            continue

        try:
            payload = _build_notion_payload(marker, result.band, result.impact_score)
            resp = _notion_post(payload, token)
        except urllib.error.HTTPError as exc:
            failed += 1
            record = {
                "timestamp": _utc_now_iso(),
                "kind": "recovery_http_error",
                "status": exc.code,
                "error": str(exc),
                "marker": marker,
                "recovered_from": pending.get("timestamp"),
            }
            _append_recovery_record(record)
            results.append(record)
            continue
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            failed += 1
            record = {
                "timestamp": _utc_now_iso(),
                "kind": "recovery_transport_error",
                "error": str(exc),
                "marker": marker,
                "recovered_from": pending.get("timestamp"),
            }
            _append_recovery_record(record)
            results.append(record)
            continue

        succeeded += 1
        record = {
            "timestamp": _utc_now_iso(),
            "kind": "auto_posted",
            "marker": marker,
            "band": result.band,
            "impact_score": result.impact_score,
            "notion_page_id": resp.get("id"),
            "notion_url": resp.get("url"),
            "recovered_from": pending.get("timestamp"),
        }
        _append_recovery_record(record)
        results.append(record)

    summary = {
        "unresolved_count": len(unresolved),
        "recovered": succeeded,
        "failed": failed,
        "results": results if args.json else None,
    }
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"Recovery complete: {succeeded} succeeded, {failed} failed (of {len(unresolved)})")
        for r in results:
            kind = r.get("kind")
            if kind == "auto_posted":
                print(f"  ✓ {_marker_key(r.get('marker', {}))} -> {r.get('notion_url')}")
            else:
                print(f"  ✗ {_marker_key(r.get('marker', {}))} [{kind}]: {r.get('error', '')}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
