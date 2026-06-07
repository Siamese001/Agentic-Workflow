#!/usr/bin/env python3
"""
plan_registration_weekly_report.py — Weekly drift report (§36).

Scans both directions of the Plan↔Notion registration mapping and reports:
  - On-disk plans (`docs/archive/windsurf/legacy-tree/plans/*.md`) without a Notion Plans row.
  - Notion Plans rows with Status in {Live, Draft, Waiting} whose ``Exists On Disk``
    checkbox is true but whose file is actually missing from the working tree.
  - Stale items in the registration queue (``registered=false`` older than 7 days).

Emits a Markdown report under ``docs/reports/plan_registration/<YYYY-Www>.md``.
Refreshes the shared cache at ``.claude/state/plan_registration_cache.json``
as a side effect so other gates can read a fresh snapshot.

CLI::

    python ops_scripts/calibration/plan_registration_weekly_report.py
    python ops_scripts/calibration/plan_registration_weekly_report.py --out path/to/report.md

Exit codes:
    0 — report written (drift is informational, not a failure)
    2 — Notion fetch error AND no existing cache (no report possible)

Constitutional tie-in: §36.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HELPER_PATH = REPO_ROOT / ".claude" / "governance/scripts" / "_legacy_windsurf" / "_plan_registration.py"
GATE_PATH = REPO_ROOT / "ops_scripts" / "ci" / "check_plan_registration_freshness.py"
REPORT_DIR = REPO_ROOT / "docs" / "reports" / "plan_registration"


def _load_helper():
    mod_name = "_plan_registration"
    if mod_name in sys.modules:
        return sys.modules[mod_name]
    spec = importlib.util.spec_from_file_location(mod_name, HELPER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load _plan_registration helper")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception:
        sys.modules.pop(mod_name, None)
        raise
    return mod


def _load_gate():
    """Reuse the gate module's _refresh_cache fetcher to avoid duplication."""
    mod_name = "_plan_registration_gate"
    if mod_name in sys.modules:
        return sys.modules[mod_name]
    spec = importlib.util.spec_from_file_location(mod_name, GATE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load gate module")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception:
        sys.modules.pop(mod_name, None)
        raise
    return mod


def _iso_week(now: datetime | None = None) -> str:
    if now is None:
        now = datetime.now(timezone.utc)
    year, week, _ = now.isocalendar()
    return f"{year}-W{week:02d}"


def _parse_iso(s: str) -> datetime | None:
    if not s or not isinstance(s, str):
        return None
    try:
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=None,
                        help="Report output path (default docs/reports/plan_registration/<iso-week>.md)")
    parser.add_argument("--stale-days", type=int, default=7,
                        help="Flag queue rows unregistered longer than this (default 7)")
    args = parser.parse_args(argv)

    helper = _load_helper()
    gate = _load_gate()

    # Refresh cache (best-effort).
    count, err = gate._refresh_cache(helper)
    cache = helper.read_cache()
    if cache is None:
        print(
            f"[plan_registration_weekly_report] ERROR — no cache and refresh failed ({err})",
            file=sys.stderr,
        )
        return 2

    drift = helper.drift_report(cache=cache)
    on_disk_missing = drift["on_disk_not_in_notion"]
    notion_orphans = drift["notion_active_not_on_disk"]

    # Stale queue entries.
    stale_cutoff = datetime.now(timezone.utc) - timedelta(days=args.stale_days)
    stale_queue: list[dict] = []
    for row in helper.pending_registrations():
        ts = _parse_iso(row.get("captured_at", ""))
        if ts is not None and ts < stale_cutoff:
            stale_queue.append(row)

    week = _iso_week()
    out_path = args.out or (REPORT_DIR / f"{week}.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    refresh_note = (
        f"cache refreshed ({count} Notion Plans rows)" if err is None
        else f"cache refresh failed ({err}); using prior snapshot"
    )

    lines: list[str] = []
    lines.append(f"# Plan Registration Drift Report — {week}")
    lines.append("")
    lines.append(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    lines.append(f"Cache:     {refresh_note}")
    lines.append("")
    lines.append("Constitutional §36 — plan-Notion registration. See "
                 "`.claude/rules/plan-registration-enforcement.md`.")
    lines.append("")

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- On-disk plans missing Notion row: **{len(on_disk_missing)}**")
    lines.append(f"- Notion Live/Draft/Waiting rows without on-disk file: **{len(notion_orphans)}**")
    lines.append(f"- Stale queue entries (> {args.stale_days} days unregistered): **{len(stale_queue)}**")
    lines.append("")

    lines.append("## On-Disk Plans Missing Notion Row")
    lines.append("")
    if not on_disk_missing:
        lines.append("_None._")
    else:
        for slug in on_disk_missing:
            lines.append(f"- `{slug}` — `docs/archive/windsurf/legacy-tree/plans/{slug}.md`")
    lines.append("")

    lines.append("## Notion Orphans (Active Row, No File)")
    lines.append("")
    if not notion_orphans:
        lines.append("_None._")
    else:
        plans_map = cache.get("plans") or {}
        for slug in notion_orphans:
            entry = plans_map.get(slug) or {}
            status = entry.get("status", "?")
            lines.append(f"- `{slug}` — Status={status}, page_id={entry.get('page_id', '?')}")
    lines.append("")

    lines.append("## Stale Queue Entries")
    lines.append("")
    if not stale_queue:
        lines.append("_None._")
    else:
        for row in stale_queue:
            lines.append(
                f"- `{row.get('slug')}` — captured {row.get('captured_at')}, "
                f"declared_status={row.get('declared_status')}"
            )
    lines.append("")

    lines.append("## Remediation")
    lines.append("")
    lines.append("- For on-disk-missing-Notion: `API-post-page` into Plans DB "
                 "(data source `ac53d31b-3068-4039-9ebe-856c12caab32`).")
    lines.append("- For Notion orphans: either restore the plan file OR flip Status to "
                 "Retired/Archived and clear `Exists On Disk`.")
    lines.append("- For stale queue entries: register via Notion OR remove the slug from "
                 "`.claude/state/plan_registration_queue.jsonl` if the plan was retracted.")
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[plan_registration_weekly_report] wrote {out_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
